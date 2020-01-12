import datetime
import os
import subprocess
from pathlib import Path

import PySimpleGUI as sg
from docx import Document

from main import generate_patient_list
from teams import TEAMS

sg.theme("Dark Blue 3")

layout = [
    [sg.Text("Choose input file:")],
    [
        sg.InputText(disabled=True, key="input_filename", enable_events=True),
        sg.FileBrowse(
            file_types=(("Word Documents", "*.docm"), ("Word Documents", "*.docx"))
        ),
    ],
    [sg.Text("Select a team:")],
    [
        sg.Combo(
            sorted(team for team in TEAMS.values()),
            enable_events=True,
            key="selected_team",
        )
    ],
    [sg.Text("Output folder:")],
    [sg.InputText(disabled=True, key="output_folder_name")],
    [sg.Text("Output filename:")],
    [sg.InputText(disabled=True, key="output_filename")],
    [
        sg.Button("Generate List", key="generate_list"),
        sg.Button("Open Output Folder", key="open_output_folder"),
    ],
]

main_window = sg.Window("Patient List Generator", layout)

while True:
    event, values = main_window.read()
    print(event, values)
    if event is None:
        break

    if event == "input_filename":
        path = Path(values["input_filename"])
        parent_path = str(path.parent)
        file_ext = path.suffix

        main_window["output_folder_name"].update(parent_path)
        if not values["selected_team"]:
            main_window["output_filename"].update(
                f"{datetime.datetime.today():%d-%m-%y}{file_ext}"
            )
        else:
            selected_team = values["selected_team"]
            main_window["output_filename"].update(
                f"{datetime.datetime.today():%d-%m-%y}_{selected_team.name.value.lower()}{file_ext}"
            )

    if event == "selected_team":
        selected_team = values["selected_team"]
        if not values["input_filename"]:
            continue
        path = Path(values["input_filename"])
        file_ext = path.suffix
        main_window["output_filename"].update(
            f"{datetime.datetime.today():%d-%m-%y}_{selected_team.name.value.lower()}{file_ext}"
        )

    if event == "open_output_folder":
        if not values["output_folder_name"]:
            continue

        path = values["output_folder_name"]

        if os.name == "nt":
            # Windows
            os.startfile(path)
        else:
            # Linux
            subprocess.Popen(["xdg-open", path])

    if event == "generate_list":
        if values["selected_team"] and values["input_filename"]:
            team = values["selected_team"]
            input_filename = Path(values["input_filename"]).name
            doc = Document(input_filename)

            generate_patient_list(team=team, doc=doc)
