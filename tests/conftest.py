from pathlib import Path

import pytest

from src.front_end import callbacks  # noqa required to avoid circular imports
from src.list_generator.models import HandoverList, PatientList
from src.shared_enums import Team, Ward
from src.shared_models import Patient
from src.front_end.app import db


@pytest.fixture
def empty_list():
    team = Team.RESPIRATORY.value
    file = Path(__file__).parent / "assets" / "empty_list.docm"
    filename = "empty_list.docm"
    return HandoverList(team, file, filename)


@pytest.fixture
def trakcare_bed_format():
    return [
        # Alex
        (Ward.ALEXANDRA, "Bay 3", "Bed F", "3F"),
        (Ward.ALEXANDRA, "Room 2", "Bed 1", "SR2"),
        # Caroline Thorpe
        (Ward.CAROLINE_THORPE, "Bay 02 CT", "Bed01", "Bay 2 Bed 1"),
        (Ward.CAROLINE_THORPE, "Room 04 CT", "Bed01", "SR4"),
        # TODO: Childrens Admission Unit
        # TODO: HDU
        # Capener incl. LBOC
        (Ward.CAPENER, "Bay 03 CA", "BedD", "3D"),
        (Ward.CAPENER, "Room 07 CA", "Bed01", "SR7"),
        (Ward.CAPENER, "Lundy Bay on Capener Ward", "Bed1F", "LBOC F"),
        # Day Surgery Unit
        (Ward.DAY_SURGERY_UNIT, "DSU Bay 03", "BEDF", "3F"),
        (Ward.DAY_SURGERY_UNIT, "DSU Room 02", "BED01", "SR2"),
        # Fortescue
        (Ward.FORTESCUE, "Yellow (FORT)", "Bed01", "Yellow 1"),
        (Ward.FORTESCUE, "Green (FORT)", "Bed02", "Green 2"),
        (Ward.FORTESCUE, "Lilac (FORT)", "Bed03", "Lilac 3"),
        (Ward.FORTESCUE, "Blue (FORT)", "Bed04", "Blue 4"),
        (Ward.FORTESCUE, "Pink (FORT)", "Bed05", "Pink 5"),
        (Ward.FORTESCUE, "Lilac Room (FORT)", "Bed01", "SR Lilac"),
        (Ward.FORTESCUE, "Yellow Room (FORT)", "Bed01", "SR Yellow"),
        (Ward.FORTESCUE, "Blue Room (FORT)", "Bed01", "SR Blue"),
        (Ward.FORTESCUE, "Pink Room (FORT)", "Bed01", "SR Pink"),
        # Glossop
        (Ward.GLOSSOP, "Bay 03 GL", "BedF", "3F"),
        (Ward.GLOSSOP, "Room 13 GL", "Bed01", "SR13"),
        # KGV
        (Ward.KGV, "KGV Bay 05", "BedD", "5D"),
        (Ward.KGV, "KGV Room 05", "Bed01", "SR5"),
        # TODO: AAA
        # Lundy
        (Ward.LUNDY, "Bay 1 LU", "BedA", "1A"),
        (Ward.LUNDY, "Room 02 LU", "Bed01", "SR2"),
        # TODO: Lundy HDU
        # Roborough
        (Ward.ROBOROUGH, "Room 10 RO", "Bed10", "SR10"),
        # TODO: how do the Flex Beds work?
        # Staples
        (Ward.STAPLES, "Bay 03 STA", "Bed E", "3E"),
        (Ward.STAPLES, "Bay 4 STA", "Bed E", "4E"),
        (Ward.STAPLES, "Room 1 STA", "Bed 1", "SR1"),
        (Ward.STAPLES, "Room 2 STA", "Bed 2", "SR2"),
        # Tarka
        (Ward.TARKA, "Bay 02 TA", "Bed2B", "2B"),
        (Ward.TARKA, "Bay 03 TA", "Bed3A", "3A"),
        (Ward.TARKA, "Tarka Room 02", "Bed01", "SR2"),
        (Ward.TARKA, "Room 04 TA", "Bed01", "SR4"),
        # Victoria
        (Ward.VICTORIA, "Bay 01 VIC", "BedA", "1A"),
        (Ward.VICTORIA, "Room 10 VIC", "Bed01", "SR10"),
        (Ward.VICTORIA, "Room 11 VIC", "Bed01", "SR11"),
        (Ward.VICTORIA, "Discharge Area VIC", None, "DA"),
    ]


@pytest.fixture
def trakcare_sideroom_format():
    # Ward, Trakcare room, Trakcare bed, bool(is_sideroom)
    return [
        (Ward.FORTESCUE, "Yellow Room (FORT)", "Bed01", True),
        (Ward.FORTESCUE, "Green (FORT)", "Bed03", False),
        (Ward.GLOSSOP, "Bay 01 GL", "BedF", False),
        (Ward.GLOSSOP, "Room 13 GL", "Bed01", True),
    ]


@pytest.fixture
def patient():
    return Patient("111 111 1111")


@pytest.fixture
def empty_patient_list():
    return PatientList(home_ward=Ward.GLOSSOP)


def add_patient_to_trak():
    stmt = """
    INSERT INTO vwPathologyCurrentInpatients (RegNumber, NHSNumber, Forename, Surname, AdmissionDate, DateOfBirth, Ward, Room, Bed, ReasonForAdmission, Consultant)
    VALUES ('123456', '1234567899', 'John', 'Smith', '2020-06-15', '1956-05-14', 'Capener', 'Room 07 CA', 'Bed01', 'Unwell', 'Dr Alison Moody');
    """  # noqa

    with db.engine.connect() as conn:
        conn.execute(stmt)


def clear_db():
    Patient.query.delete()
    db.session.commit()


def get_header_text(handover_list):
    return " ".join(paragraph.text for paragraph in handover_list.doc.sections[0].header.paragraphs)


def get_footer_text(handover_list):
    return " ".join(paragraph.text for paragraph in handover_list.doc.sections[0].footer.paragraphs)


def get_first_patient_row(handover_list):
    table = handover_list._handover_table
    return table.rows[2]  # skip header and ward name
