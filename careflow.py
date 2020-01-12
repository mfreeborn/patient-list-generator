import asyncio
import datetime
import os
from functools import partial

from aiohttp import ClientSession
from bs4 import BeautifulSoup as bs

from enums import Ward
from teams import Team
from utils import Location, Patient, PatientList

CAREFLOW_URL = "https://connect.careflowapp.com/#/SignIn"
AUTH_URL = "https://connect.careflowapp.com/authenticate"


bs = partial(bs, features="html.parser")


async def main(team: Team):
    async with ClientSession() as s:
        async with s.get(CAREFLOW_URL) as resp:
            soup = bs(await resp.text())
            csrf_token = soup.select_one("[name='csrf-token']").attrs["content"]
            s._default_headers["CSRF-Token"] = csrf_token

        payload = {
            "client_id": "DocComMobile",
            "emailAddress": os.environ.get("CAREFLOW_USERNAME"),
            "password": os.environ.get("CAREFLOW_PASSWORD"),
            "redirect_uri": "http://careflowconnect.com",
            "response_type": "token",
        }

        async with s.post(AUTH_URL, json=payload) as resp:
            token = resp.headers["access_token"]
            s._default_headers["Authorization"] = f"Bearer  {token}"

        url = "https://appapi.careflowapp.com/patients/SearchForPatientsByPopulation"

        consultants = team.consultants
        patient_list = PatientList(home_ward=team.home_ward)

        params = {
            "networkId": 1123,
            "clinician": "",
            "site": "",
            "area": "",
            "skip": 0,
            "take": 50,
        }
        for consultant in consultants:
            params["clinician"] = consultant.value
            allowed_wards = {ward.value for ward in Ward}
            async with s.get(url, params=params) as resp:
                data = await resp.json()
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
                    if pt["AreaName"]
                    != "Medical Assessment Unit"  # ignore patients on MAU
                    and pt["AreaName"]
                    in allowed_wards  # ignore random test patients stuck on the system in fake wards
                    and pt["Bed"]  # patient must have a bed allocation
                ]

                patient_list.extend(patients)
    return patient_list


def get_careflow_patients(team: Team):
    return asyncio.run(main(team=team))


if __name__ == "__main__":
    asyncio.run(main())
