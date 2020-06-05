import logging
from typing import List

from app import enums, models, teams, utils

logger = logging.getLogger("PLG")


def get_trakcare_patients(team: teams.Team) -> List[models.Patient]:
    """Return all patients on TrakCare under a given team."""

    consultants = [consultant.value for consultant in team.consultants]
    allowed_wards = [ward.value for ward in enums.Ward]

    all_patients_statement = f"""
        SELECT
            NHSNumber AS nhs_number,
            Surname AS surname,
            Forename AS forename,
            DateOfBirth AS dob,
            Ward AS ward,
            Room AS room,
            Bed AS bed,
            Consultant AS consultant,
            ReasonForAdmission AS reason_for_admission,
            AdmissionDate AS admission_date
        FROM
            vwPathologyCurrentInpatients
        WHERE
            consultant IN ({", ".join("?" * len(consultants))})
            AND
            ward IN ({", ".join("?" * len(allowed_wards))})
        """

    conn = utils.connect_to_db()
    with conn.cursor() as cursor:
        patients = cursor.execute(all_patients_statement, consultants + allowed_wards).fetchall()

    return [models.Patient.from_trakcare(patient) for patient in patients]
