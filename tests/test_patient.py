from datetime import date

import pytest

from app.enums import Ward
from app.patient import Location, Patient, PatientList


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


def test_patient_equality():
    pt_1 = Patient("111 111 1111")
    pt_2 = Patient("111 111 1111")
    pt_3 = Patient("222 222 2222")

    assert pt_1 == pt_2
    assert pt_1 != pt_3
    assert pt_2 != pt_3


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


def test_patient_bed(patient):
    patient.location = Location(Ward.GLOSSOP, "GLOBAY04", "BedE")
    expected = "4E"

    assert patient.bed == expected


def test_merge_patients(patient):
    pt_dict = {
        "given_name": "Ronald",
        "surname": "O'Sullivan",
        "dob": date.today(),
        "reason_for_admission": "Aspiration pneumonia",
        "jobs": "Chase CXR",
        "edd": "Wed",
        "tta": "yes",
        "ds": "no",
        "bloods": "7",
    }
    location_1 = Location(Ward.GLOSSOP, "GLOBAY04", "BedE")
    location_2 = Location(Ward.CAPENER, "CAPBAY02", "BedA")

    # start with a patient just with the up to date details from CareFlow
    patient.given_name = pt_dict["given_name"]
    patient.surname = pt_dict["surname"]
    patient.dob = pt_dict["dob"]
    patient.location = location_1

    # make the same patient, who is on the handover list, with all their jobs etc
    patient2 = Patient("111 111 1111", location=location_2, **pt_dict)

    # merge them together
    patient.merge(patient2)

    # ensure that the resulting patient has all of the attributes taken from the handover list
    # but is also in the up to date location according to CareFlow
    for attr in pt_dict:
        assert getattr(patient, attr) == pt_dict[attr]

    assert patient.location == location_1


def test_merge_fails_with_diff_patients(patient):
    pt_dict = {
        "given_name": "Ronald",
        "surname": "O'Sullivan",
        "dob": date.today(),
        "reason_for_admission": "Aspiration pneumonia",
        "jobs": "Chase CXR",
        "edd": "Wed",
        "ds": "no",
        "tta": "yes",
        "bloods": "7",
    }
    location_1 = Location(Ward.GLOSSOP, "GLOBAY04", "BedE")
    location_2 = Location(Ward.CAPENER, "CAPBAY02", "BedA")

    # start with a patient just with the up to date details from CareFlow
    patient.given_name = pt_dict["given_name"]
    patient.surname = pt_dict["surname"]
    patient.dob = pt_dict["dob"]
    patient.location = location_1

    # make a different patient, who is on the handover list, with all their jobs etc
    patient2 = Patient("222 222 2222", location=location_2, **pt_dict)

    # merge them together
    with pytest.raises(ValueError):
        patient.merge(patient2)


def test_patient_from_table_row():
    class Cell:
        def __init__(self, contents):
            self.text = contents

    class Row:
        def __init__(self, row):
            self.cells = [Cell(text) for text in row]

    row = [
        "1A",  # location
        f"ALLEN, Mark\n{date.today():%d/%m/%Y} (0 Yrs)\n111 111 1111",  # patient details
        "Aspiration pneumonia",  # reason for admission
        "Chase CXR",  # jobs
        "Wed",  # edd
        "no",  # ds
        "yes",  # tta
        "7",  # bloods
    ]

    pt = Patient.from_table_row(Row(row))

    pt_dict = {
        "reason_for_admission": "Aspiration pneumonia",
        "jobs": "Chase CXR",
        "edd": "Wed",
        "ds": "no",
        "tta": "yes",
        "bloods": "7",
    }

    for attr in pt_dict:
        assert getattr(pt, attr) == pt_dict[attr]

    row[1] = "pt details with no nhs number"

    with pytest.raises(ValueError):
        Patient.from_table_row(Row(row))


def test_patient_list_append(empty_patient_list, patient):
    x = empty_patient_list.append(patient)

    assert x is None
    assert empty_patient_list.patients == [patient]


def test_patient_list_extend(empty_patient_list, patient):
    patient_2 = Patient("222 222 2222")

    x = empty_patient_list.extend([patient, patient_2])

    assert x is None
    assert empty_patient_list.patients == [patient, patient_2]


def test_patient_list_append_fail(empty_patient_list):
    with pytest.raises(TypeError):
        empty_patient_list.append("This is not a valid patient")


def test_patient_list_extend_fail(empty_patient_list):
    with pytest.raises(TypeError):
        empty_patient_list.extend(["This is not a valid patient", "Neither is this"])


def test_patient_list_remove_duplicates(empty_patient_list, patient):
    empty_patient_list.extend([patient, patient])

    assert empty_patient_list.patients == [patient]


def test_patient_list_search_by_nhs_num(empty_patient_list, patient):
    empty_patient_list.append(patient)

    # get either by Patient or NHS number
    assert empty_patient_list[patient] is patient
    assert empty_patient_list[patient.nhs_number] is patient


def test_patient_list_contains_patient(empty_patient_list, patient):
    empty_patient_list.append(patient)

    # search either by Patient or NHS number
    assert patient in empty_patient_list
    assert patient.nhs_number in empty_patient_list


def test_patient_list_len(empty_patient_list, patient):
    assert len(empty_patient_list) == 0

    empty_patient_list.append(patient)
    assert len(empty_patient_list) == 1


def test_patient_list_iter(empty_patient_list, patient):
    patient_2 = Patient("222 222 2222")

    empty_patient_list.extend([patient, patient_2])

    for list_pt, other_pt in zip(empty_patient_list, [patient, patient_2]):
        assert list_pt == other_pt
