import datetime
import os
import subprocess
from pathlib import Path

import PySimpleGUI as sg

from main import main
from teams import TEAMS

sg.theme("Dark Blue 3")

layout = [
    [sg.Text("Choose input file:")],
    [
        sg.InputText(
            size=(55, 1), disabled=True, key="input_file_path", enable_events=True
        ),
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
    [
        sg.InputText(size=(55, 1), disabled=True, key="output_folder_path"),
        sg.FolderBrowse(),
    ],
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

    if event == "input_file_path":
        path = Path(values["input_file_path"])
        parent_path = path.parent
        file_ext = path.suffix

        today = datetime.date.today()
        main_window["output_folder_path"].update(parent_path)
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
        if not values["input_file_path"]:
            continue
        path = Path(values["input_file_path"])
        file_ext = path.suffix
        main_window["output_filename"].update(
            f"{datetime.datetime.today():%d-%m-%Y}_{selected_team.name.value.lower()}{file_ext}"
        )

    if event == "open_output_folder":
        if not values["output_folder_path"]:
            continue

        path = values["output_folder_path"]

        if os.name == "nt":
            # Windows
            os.startfile(path)
        else:
            # Linux
            subprocess.Popen(["xdg-open", path])

    if event == "generate_list":
        if values["selected_team"] and values["input_file_path"]:
            team = values["selected_team"]
            input_file_path = Path(values["input_file_path"])
            output_file_path = (
                Path(values["output_folder_path"]) / values["output_filename"]
            )

            print(input_file_path)
            print(output_file_path)

            main(
                team=team,
                input_file_path=input_file_path,
                output_file_path=output_file_path,
            )
