import pytest
from app.enums import Ward
from app.models import Patient, PatientList


@pytest.fixture
def careflow_bed_format():
    return [
        # Alex
        (Ward.ALEXANDRA, "ALEBAY03", "Bed A", "3A"),
        (Ward.ALEXANDRA, "ALESR06", "Bed 1", "SR6"),
        # Capener
        (Ward.CAPENER, "CAPBAY03", "BedA", "3A"),
        (Ward.CAPENER, "CAPSR06", "Bed01", "SR6"),
        # Fortescue
        (Ward.FORTESCUE, "FOR2YELLOW", "Bed01", "Yellow 1"),
        (Ward.FORTESCUE, "FOR2GREENBAY", "Bed02", "Green 2"),
        (Ward.FORTESCUE, "FOR3LILACBAY", "Bed03", "Lilac 3"),
        (Ward.FORTESCUE, "FOR4BLUEBAY", "Bed04", "Blue 4"),
        (Ward.FORTESCUE, "FOR5PINKBAY", "Bed05", "Pink 5"),
        (Ward.FORTESCUE, "FORLILACRM", "Bed01", "SR Lilac"),
        (Ward.FORTESCUE, "FORYELLOWRM", "Bed01", "SR Yellow"),
        (Ward.FORTESCUE, "FORBLUERM", "Bed01", "SR Blue"),
        (Ward.FORTESCUE, "FORPINKRM", "Bed01", "SR Pink"),
        # Glossop
        (Ward.GLOSSOP, "GLOBAY03", "BedF", "3F"),
        (Ward.GLOSSOP, "GLOSR13", "Bed01", "SR13"),
        # KGV
        (Ward.KGV, "KGVBAY05", "BedB", "5B"),
        (Ward.KGV, "KGVSR07", "Bed01", "SR7"),
        # Lundy
        (Ward.LUNDY, "CAPBAY01", "Bed1C", "1C"),
        (Ward.LUNDY, "LUNBAY02", "BedB", "2B"),
        (Ward.LUNDY, "LUNSR02", "Bed01", "SR2"),
        # Roborough
        (Ward.ROBOROUGH, "ROBSR02", "Bed02", "SR2"),
        # Staples
        (Ward.STAPLES, "STABAY01", "Bed A", "1A"),
        (Ward.STAPLES, "STASR02", "Bed 2", "SR2"),
        # Tarka
        (Ward.TARKA, "TARBAY02", "Bed2D", "2D"),
        (Ward.TARKA, "TARSR08", "Bed01", "SR8"),
        # Victoria
        (Ward.VICTORIA, "VICBAY02", "BedA", "2A"),
        (Ward.VICTORIA, "VICSR08", "Bed01", "SR8"),
    ]


@pytest.fixture
def trakcare_bed_format():
    return [
        # Alex
        (Ward.ALEXANDRA, "Bay 3", "Bed F", "3F"),
        (Ward.ALEXANDRA, "Room 2", "Bed 1", "SR2"),
        # Caroline Thorpe
        (Ward.CAROLINE_THORPE, "Bay 02 CT", "Bed01", "B2 B1"),
        (Ward.CAROLINE_THORPE, "Room 04 CT", "Bed01", "SR4"),
        # TODO: Childrens Admission Unit
        # TODO: HDU
        # Capener incl. LBOC
        (Ward.CAPENER, "Bay 03 CA", "BedD", "3D"),
        (Ward.CAPENER, "Room 07 CA", "Bed01", "SR7"),
        (Ward.CAPENER, "Lundy Bay on Capener Ward", "Bed1F", "LBOC F"),
        # Fortescue
        (Ward.FORTESCUE, "Yellow (FORT)", "Bed01", "Yell 1"),
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
        (Ward.VICTORIA, "Room 11 VIC", "Bed01", "SR11"),
        (Ward.VICTORIA, "Room 11 VIC", "Bed01", "SR11"),
        (Ward.VICTORIA, "Discharge Area VIC", None, "DA"),
    ]


@pytest.fixture
def patient():
    return Patient("111 111 1111")


@pytest.fixture
def empty_patient_list():
    return PatientList(home_ward=Ward.GLOSSOP)
