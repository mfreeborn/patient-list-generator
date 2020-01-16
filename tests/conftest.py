import pytest
from app.enums import Ward
from app.patient import Patient


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
def patient():
    return Patient("111 111 1111")
