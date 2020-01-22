import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from requests_html import HTMLSession

from app.enums import Ward
from app.exceptions import (
    CareFlowAuthorisationError,
    CareFlowError,
    NoCareFlowCredentialsError,
)
from app.gui.enums import Key
from app.patient import Patient, PatientList
from app.teams import Team

CAREFLOW_URL = "https://connect.careflowapp.com/#/SignIn"
AUTH_URL = "https://connect.careflowapp.com/authenticate"


def _login_to_careflow(session, credentials):
    logging.debug("Logging into CareFlow")
    username, password = (
        credentials.get(Key.CAREFLOW_USERNAME_INPUT),
        credentials.get(Key.CAREFLOW_PASSWORD_INPUT),
    )

    if not (username and password):
        raise NoCareFlowCredentialsError(
            "Credentials for logging into Careflow are missing."
        )

    r = session.get(CAREFLOW_URL)
    csrf_token = r.html.find("[name='csrf-token']", first=True).attrs["content"]
    session.headers.update({"CSRF-Token": csrf_token})

    payload = {
        "client_id": "DocComMobile",
        "emailAddress": username,
        "password": password,
        "redirect_uri": "http://careflowconnect.com",
        "response_type": "token",
    }

    r = session.post(AUTH_URL, json=payload)

    try:
        token = r.headers["access_token"]
    except KeyError:
        raise CareFlowAuthorisationError(
            "Error logging into Careflow, are your credentials definitely correct?"
        )

    session.headers.update({"Authorization": f"Bearer  {token}"})
    return session


def _fetch_patients_by_consultant(session, consultant) -> list:
    logging.debug("Fetching patients under %s", consultant.value)
    start = time.time()
    pt_search_url = (
        "https://appapi.careflowapp.com/patients/SearchForPatientsByPopulation"
    )

    search_params = {
        "networkId": 1123,
        "clinician": consultant.value,
        "skip": 0,
        "take": 50,
    }

    allowed_wards = {ward.value for ward in Ward}

    r = session.get(pt_search_url, params=search_params)
    data = r.json()
    patients = data["Data"]["Patients"]
    patients = [
        Patient.from_careflow_api(pt)
        for pt in patients
        if pt["AreaName"] in allowed_wards  # ignore patients on e.g. MAU and ITU
        and pt["Bed"]  # patient must have a bed allocation
    ]
    logging.debug(
        "%d patients found under %s in %.2fs",
        len(patients),
        consultant.value,
        time.time() - start,
    )
    return patients


def _main(team: Team, credentials: dict):
    with HTMLSession() as s:
        _login_to_careflow(s, credentials)

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(_fetch_patients_by_consultant, s, consultant)
                for consultant in team.consultants
            ]

        patient_list = PatientList(home_ward=team.home_ward)
        for future in as_completed(futures):
            patient_list.extend(future.result())

    return patient_list


def get_careflow_patients(team: Team, credentials: dict):
    try:
        start = time.time()
        careflow_pts = _main(team=team, credentials=credentials)
    # re-raise any specific exceptions first, before raising a generic exception
    except (CareFlowAuthorisationError, NoCareFlowCredentialsError):
        raise
    except Exception as e:  # noqa
        logging.exception(e)
        raise CareFlowError("Error getting patients from CareFlow")
    else:
        logging.debug("TOTAL: %.2fs", time.time() - start)
        return careflow_pts
