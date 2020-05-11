import logging

from app.exceptions import NoTrakCareCredentialsError, TrakCareAuthorisationError
from app.gui.enums import Key
from app.patient import Patient, PatientList
from app.utils import connect_to_db

logger = logging.getLogger("PLG")


def get_trakcare_patients() -> PatientList:
    """Return all patients on TrakCare."""
    conn = connect_to_db()
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
        FROM vwPathologyCurrentInpatients
        """
    patients = cursor.execute(all_patients_statement).fetchall()
