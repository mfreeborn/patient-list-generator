from docx import Document

from teams import Team
from utils import Patient, PatientList

input_list = Document("31.12.2019.docm").tables[0]


def get_list_patients(team: Team):
    pt_list = PatientList(home_ward=team.home_ward)

    current_ward = None
    for row in input_list.rows:
        # skip past the headers
        if row.cells[0].text.lower() == "bed":
            continue

        # update the current ward we are on. The name of the ward is repeated
        # across all the cells as the cells were all merged together
        if row.cells[0].text.lower() == row.cells[1].text.lower():
            current_ward = row.cells[0].text
            continue

        pt = Patient.from_table_row(row, current_ward)

        pt_list.append(pt)

    return pt_list
