from app.patient import Location, Patient
from app.enums import Ward
from datetime import date


def test_location_parse_beds(careflow_bed_format):
    for ward, cf_bay, cf_bed, list_bed in careflow_bed_format:
        assert Location(ward, cf_bay, cf_bed).bed == list_bed


def test_location_lun_ward_on_cap():
    # so-called "Lundy Ward On Capener" has a ward of Lundy by default,
    # but should have a ward of Capener
    location = (Ward.LUNDY, "CAPBAY01", "Bed1C")
    loc = Location(location[0], location[1], location[2])
    assert loc.ward == Ward.CAPENER


def test_location_is_sideroom():
    locs = [
        (Ward.FORTESCUE, "FORYELLOWRM", "Bed01", True),
        (Ward.FORTESCUE, "FOR2GREEN", "Bed03", False),
        (Ward.GLOSSOP, "GLOBAY01", "BedF", False),
        (Ward.GLOSSOP, "GLOSR13", "Bed01", True),
    ]

    for ward, cf_bay, cf_bed, is_sr in locs:
        loc = Location(ward, cf_bay, cf_bed)
        assert loc.is_sideroom == is_sr


def test_patient_consistent_nhs_num():
    nhs_nums = ["1111111111", "111 111 1111", "1 1 11 1 11111"]
    expected = "111 111 1111"

    for nhs_num in nhs_nums:
        assert Patient(nhs_num).nhs_number == expected


def test_patient_age(patient):
    assert patient.age is None

    today = date.today()
    patient.dob = today
    assert patient.age == 0

    patient.dob = today.replace(year=today.year - 50)
    assert patient.age == 50


def test_patient_name(patient):
    expected = "UNKNOWN, Unknown"
    assert patient.list_name == expected

    names = [
        ("Michael", "Freeborn", "FREEBORN, Michael"),
        ("mary-jane", "smith", "SMITH, Mary-Jane"),
        (
            "Maximillian",
            "Throborough-Longbottom",
            "THROBOROUGH-LONGBOTTOM, Maximillian",
        ),
    ]

    for given_name, surname, expected_list_name in names:
        patient.given_name = given_name
        patient.surname = surname
        assert patient.list_name == expected_list_name


def test_patient_details(patient):
    expected = "UNKNOWN"
    assert patient.patient_details == expected

    patient.dob = date.today()
    patient.given_name = "Mark"
    patient.surname = "Allen"

    expected = f"ALLEN, Mark\n{date.today():%d/%m/%Y} (0 Yrs)\n111 111 1111"

    assert patient.patient_details == expected
