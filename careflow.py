import datetime
from exceptions import (
    CareFlowError,
    NoCareFlowCredentialsError,
    CareFlowAuthorisationError,
)

from requests_html import HTMLSession

from enums import Ward
from patient import Location, Patient, PatientList
from teams import Team

CAREFLOW_URL = "https://connect.careflowapp.com/#/SignIn"
AUTH_URL = "https://connect.careflowapp.com/authenticate"


def _main(team: Team, credentials: dict):
    with HTMLSession() as s:
        r = s.get(CAREFLOW_URL)
        csrf_token = r.html.find("[name='csrf-token']", first=True).attrs["content"]
        s.headers.update({"CSRF-Token": csrf_token})

        username, password = (
            credentials["careflow_username"],
            credentials["careflow_password"],
        )

        if not (username and password):
            raise NoCareFlowCredentialsError(
                "No credentials were found to log into CareFlow"
            )

        payload = {
            "client_id": "DocComMobile",
            "emailAddress": username,
            "password": password,
            "redirect_uri": "http://careflowconnect.com",
            "response_type": "token",
        }

        r = s.post(AUTH_URL, json=payload)

        try:
            token = r.headers["access_token"]
        except KeyError:
            raise CareFlowAuthorisationError(
                "Error logging into Careflow, are your credentials definitely correct?"
            )

        s.headers.update({"Authorization": f"Bearer  {token}"})

        pt_search_url = (
            "https://appapi.careflowapp.com/patients/SearchForPatientsByPopulation"
        )

        consultants = team.consultants
        patient_list = PatientList(home_ward=team.home_ward)

        search_params = {
            "networkId": 1123,
            "clinician": "",
            "skip": 0,
            "take": 50,
        }

        for consultant in consultants:
            search_params["clinician"] = consultant.value
            allowed_wards = {ward.value for ward in Ward}
            r = s.get(pt_search_url, params=search_params)
            data = r.json()
            patients = data["Data"]["Patients"]
            patients = [
                Patient(
                    given_name=pt["PatientGivenName"],
                    surname=pt["PatientFamilyName"],
                    dob=datetime.datetime.strptime(
                        pt["PatientDateOfBirth"], "%d-%b-%Y"
                    ).date(),
                    nhs_number=pt["PatientNHSNumber"],
                    location=Location(
                        ward=Ward(pt["AreaName"]), bay=pt["Bay"], bed=pt["Bed"]
                    ),
                )
                for pt in patients
                if pt["AreaName"] in allowed_wards  # ignore patients on e.g. MAU
                and pt["Bed"]  # patient must have a bed allocation
            ]

            patient_list.extend(patients)

    return patient_list


def get_careflow_patients(team: Team, credentials: dict):
    try:
        careflow_pts = _main(team=team, credentials=credentials)
    # re-raise any specific exceptions first, before raising a generic exception
    except (CareFlowAuthorisationError, NoCareFlowCredentialsError):
        raise
    except:  # noqa
        raise CareFlowError("Error getting patients from CareFlow")
    else:
        return careflow_pts
