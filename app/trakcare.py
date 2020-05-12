import logging
from typing import List

from app import enum, models, teams, utils

logger = logging.getLogger("PLG")


def get_trakcare_patients(team: teams.Team) -> List[models.Patient]:
    """Return all patients on TrakCare under a given team."""
    conn = utils.connect_to_db()
    cursor = conn.cursor()

    all_patients_statement = """
        SELECT
            NHSNumber AS nhs_number
            Surname AS surname
            Forename AS forename
            DateOfBirth AS dob
            Ward AS ward
            Room AS room
            Bed AS bed
            ResponsibleConsultant AS consultant
            ReasonForAttendance AS reason_for_attendance
        FROM
            vwPathologyCurrentInpatients
        WHERE
            consultant IN ?
            AND
            ward IN ?
        """

    consultants = team.consultants
    allowed_wards = [ward.value for ward in enum.Ward]
    return [
        models.Patient.from_trakcare(patient)
        for patient in cursor.execute(all_patients_statement, consultants, allowed_wards)
    ]
