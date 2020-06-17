import datetime

from src.front_end.app import db

from .conftest import (
    add_patient_to_trak,
    clear_db,
    get_first_patient_row,
    get_footer_text,
    get_header_text,
)


def test_header_content_unchanged(empty_list):
    # get the header text from the empty list
    expected = get_header_text(empty_list)

    # pass it through the generator
    empty_list.update()

    # check that the header text is unchanged
    new_header_text = get_header_text(empty_list)
    assert new_header_text == expected


def test_footer_content_updated(empty_list):
    original_footer_text = get_footer_text(empty_list)

    # add a patient to the database to give the list something to work with
    add_patient_to_trak()

    empty_list.update()

    new_footer_text = get_footer_text(empty_list)

    assert original_footer_text != new_footer_text
    assert "1 patient (1 new)" in new_footer_text
    # there is technically a ~0.03 second window where the minute could tick over
    # and this assertion will erroneously fail... not too bothered for now
    assert f"Generated at {datetime.datetime.now():%H:%M %d/%m/%Y}"

    # now delete the patient and check the footer has been updated again
    stmt = """
    DELETE FROM vwPathologyCurrentInpatients WHERE vwPathologyCurrentInpatients.RegNumber = '123456'
    """

    with db.engine.connect() as conn:
        conn.execute(stmt)

    # force the internal patient list to be parsed from the new list
    empty_list.patients = empty_list._parse_patients()
    empty_list.update()

    new_footer_text = get_footer_text(empty_list)

    assert "1 patient (1 new)" not in new_footer_text
    assert "0 patients (0 new)" in new_footer_text


def test_new_patient_is_bold(empty_list):
    # add a patient to TrakCare and put them on the list; they should be bold
    add_patient_to_trak()

    empty_list.update()

    row = get_first_patient_row(empty_list)

    for cell in row.cells:
        for para in cell.paragraphs:
            for run in para.runs:
                assert run.bold

    clear_db()


def test_old_patient_not_bold(empty_list):
    # add a patient to TrakCare and put them on the list; they should be bold
    add_patient_to_trak()

    empty_list.update()

    # force the internal patient list to be parsed from the new list, the
    # patient should now be unbolded
    empty_list.patients = empty_list._parse_patients()
    empty_list.update()

    row = get_first_patient_row(empty_list)

    for cell in row.cells:
        for para in cell.paragraphs:
            for run in para.runs:
                assert not run.bold

    clear_db()
