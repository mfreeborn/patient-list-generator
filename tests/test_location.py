from src.shared_enums import Ward
from src.shared_models import Location


def test_location_is_sideroom(trakcare_sideroom_format):
    for ward, cf_bay, cf_bed, is_sr in trakcare_sideroom_format:
        loc = Location(ward, cf_bay, cf_bed)
        assert loc.is_sideroom == is_sr


def test_location_parse_beds(trakcare_bed_format):
    for ward, tk_bay, tk_bed, list_bed in trakcare_bed_format:
        assert Location(ward, tk_bay, tk_bed).bed == list_bed


def test_fortescue_bed_sorting():
    expected_beds = [
        "Green 1",
        "Green 3",
        "Yellow 2",
        "Lilac 4",
        "Blue 1",
        "Blue 2",
        "Pink 5",
        "SR Green",
        "SR Yellow",
        "SR Lilac",
        "SR Blue",
        "SR Pink",
    ]
    unsorted_locations = [
        Location(Ward.FORTESCUE, "Pink (FORT)", "bed05"),
        Location(Ward.FORTESCUE, "Yellow Room (FORT)", "bed01"),
        Location(Ward.FORTESCUE, "Blue (FORT)", "bed01"),
        Location(Ward.FORTESCUE, "Lilac Room (FORT)", "bed01"),
        Location(Ward.FORTESCUE, "Green Room (FORT)", "bed01"),
        Location(Ward.FORTESCUE, "Blue Room (FORT)", "bed01"),
        Location(Ward.FORTESCUE, "Green (FORT)", "bed01"),
        Location(Ward.FORTESCUE, "Green (FORT)", "bed03"),
        Location(Ward.FORTESCUE, "Lilac (FORT)", "bed04"),
        Location(Ward.FORTESCUE, "Blue (FORT)", "bed02"),
        Location(Ward.FORTESCUE, "Pink Room (FORT)", "bed01"),
        Location(Ward.FORTESCUE, "Yellow (FORT)", "bed02"),
    ]

    sorted_locations = sorted(unsorted_locations, key=lambda location: location._bed_sort)

    assert all(
        sorted_loc.bed == expected_bed
        for expected_bed, sorted_loc in zip(expected_beds, sorted_locations)
    )


def test_non_fortescue_bed_sorting():
    expected_beds = ["1A", "1B", "2E", "3C", "4D", "4F", "SR7", "SR9", "SR10", "DA"]
    unsorted_locations = [
        Location(Ward.VICTORIA, "Bay 04 VIC", "BedD"),
        Location(Ward.VICTORIA, "Bay 03 VIC", "BedC"),
        Location(Ward.VICTORIA, "Bay 02 VIC", "BedE"),
        Location(Ward.VICTORIA, "Discharge Area VIC", None),
        Location(Ward.VICTORIA, "Room 07 VIC", "Bed01"),
        Location(Ward.VICTORIA, "Bay 01 VIC", "BedA"),
        Location(Ward.VICTORIA, "Room 10 VIC", "Bed01"),
        Location(Ward.VICTORIA, "Bay 01 VIC", "BedB"),
        Location(Ward.VICTORIA, "Room 09 VIC", "Bed01"),
        Location(Ward.VICTORIA, "Bay 04 VIC", "BedF"),
    ]

    sorted_locations = sorted(unsorted_locations, key=lambda location: location._bed_sort)

    assert all(
        sorted_loc.bed == expected_bed
        for expected_bed, sorted_loc in zip(expected_beds, sorted_locations)
    )
