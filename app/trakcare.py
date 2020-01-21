import logging

from requests_html import HTMLSession

from app.exceptions import NoTrakCareCredentialsError, TrakCareAuthorisationError
from app.gui.enums import Key
from app.patient import Patient, PatientList


def _login_to_trakcare(credentials, session):
    logging.debug("Logging into TrakCare")
    s = session
    url = "https://live.ennd.mpls.hs.intersystems.thirdparty.nhs.uk/trakcare/csp/logon.csp"

    username, password = (
        credentials.get(Key.TRAKCARE_USERNAME_INPUT),
        credentials.get(Key.TRAKCARE_PASSWORD_INPUT),
    )

    if not (username and password):
        raise NoTrakCareCredentialsError(
            "Credentials for logging into TrakCare are missing."
        )

    r = s.post(
        url,
        data={
            "USERNAME": username,
            "PASSWORD": password,
            "TEVENT": "d1473iLogon",
            "TFORM": "SSUserLogon",
            "TDIRTY": "1",
            "LocationListFlag": "1",
            "Hospital": "North Devon District Hospital",
            "LocListLocID": "882",
            "LocListGroupID": "37",
            "LocListProfileID": "36",
        },
    )

    url = "https://live.ennd.mpls.hs.intersystems.thirdparty.nhs.uk/trakcare/csp/epr.frames.csp?RELOGON=1"

    r = s.get(url)
    try:
        page_id = r.html.find("#TRAK_main", first=True).attrs["src"].split("=")[-1]
    except:  # noqa
        raise TrakCareAuthorisationError(
            "Error logging into TrakCare, are your credentials definitely correct?"
        )

    return session, page_id


def _get_reason_for_admission(patient: Patient, page_id, session) -> PatientList:
    logging.debug("Getting reason for admission for %s", patient.list_name)
    s = session
    url = "https://live.ennd.mpls.hs.intersystems.thirdparty.nhs.uk/trakcare/csp/websys.csp"

    r = s.post(
        url,
        data={
            "TFORM": "PAPerson.Find",
            "TEVENT": "d48ifind1",
            "TDIRTY": "2",
            "TWKFL": "50122",
            "TWKFLNAME": "ENXX.General Episode",
            "TWKFLI": "1",
            "LoctionTypes": "E",
            "NationalID": patient.nhs_number.replace(" ", ""),
            "TPAGID": page_id,
            "exact": "on",
            "soundex": "on",
            "regoflag": "on",
        },
    )

    episode_rows = r.html.find("#tPAAdm_Tree_1", first=True).find("tr")

    latest_inpatient_episode = None
    for row in episode_rows:
        row_text = row.text.lower()
        if "inpatient" in row_text and "current" in row_text:
            latest_inpatient_episode = row
            break
    else:
        logging.debug(
            "Failed to find current inpatient episode for %s. Is it on the second"
            "page of Patient Enquiry?",
            patient.list_name,
        )

        # search the next page
        # WEVENT = (
        #     r.html.find("#Episodez1", first=True)
        #     .attrs["onclick"]
        #     .split("websys_nested('")[1]
        #     .split("','")[0]
        # )
        # treloadid = r.html.find("#TRELOADID", first=True).attrs["value"]

        # WARG_3 = (
        #     r.html.find("SCRIPT[id^=websysPagingJS]", first=True)
        #     .text.split("_NextPage() {")[1]
        #     .split("function PAAdm_Tree_1_Reload(ExtraParams)")[0]
        #     .split("','")[-2]
        # )

        # url = "https://live.ennd.mpls.hs.intersystems.thirdparty.nhs.uk/trakcare/csp/%25CSP.Broker.cls"
        # params = {
        #     "WARGC": "4",
        #     "WEVENT": WEVENT,
        #     "WARG_1": "613:1^_1",
        #     "WARG_2": "cmp_PAAdm_Tree_1",
        #     "WARG_3": WARG_3,
        #     "WARG_4": f"&TCMP.TRELOADID={treloadid}",
        # }

        # r = s.post(url, data=params)
        # # r.html.html holds the data for the second page, but it is an incomprehensible mess

    args = latest_inpatient_episode.find("[tuid]", first=True).attrs["onclick"]
    args = args.split("('")[1].split(",")[0]

    url = (
        f"https://live.ennd.mpls.hs.intersystems.thirdparty.nhs.uk/trakcare/csp/{args}"
    )

    r = s.get(url)
    return r.html.find("#MRADMPresentComplaint", first=True).text


def get_reason_for_admissions(patients, credentials):
    with HTMLSession() as s:
        # currently this seems to need to be synchronous. It appears that a fresh
        # page_id is required for each patient
        for patient in patients:
            s, page_id = _login_to_trakcare(credentials, s)
            try:
                patient.reason_for_admission = _get_reason_for_admission(
                    patient, page_id, s
                )
            except Exception as e:
                # we'll just skip past any errors and leave the .reason_for_admission blank
                logging.exception(e)
    return patients
