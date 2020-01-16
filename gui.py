import datetime
import os
import subprocess
from pathlib import Path
from pprint import pprint

import PySimpleGUI as sg

from main import main
from teams import TEAMS, Team
from utils import log_gui

sg.theme("Dark Blue 3")

main_tab_layout = [
    [sg.Text("Choose input file:*")],
    [
        sg.InputText(
            size=(55, 1), disabled=True, key="input_file_path", enable_events=True
        ),
        sg.FileBrowse(
            file_types=(("Word Documents", "*.docm"), ("Word Documents", "*.docx"))
        ),
    ],
    [sg.Text("Select a team:*")],
    [
        sg.Combo(
            sorted(team for team in TEAMS.values()),
            enable_events=True,
            key="selected_team",
        )
    ],
    [sg.Text("Output folder:")],
    [
        sg.InputText(
            size=(55, 1), disabled=True, key="output_folder_path", enable_events=True
        ),
        sg.FolderBrowse(),
    ],
    [sg.Text("Output filename:")],
    [sg.InputText(disabled=True, key="output_filename")],
    [
        sg.Button("Generate List", key="generate_list_button", disabled=True,),
        sg.Button("Open Output Folder", key="open_output_folder", disabled=True),
    ],
    [
        sg.Text(
            "Error - please check the logs",
            key="error_text",
            visible=False,
            font=("Helvetica", 12, "bold"),
        )
    ],
]

log_tab_layout = [
    [sg.Output(key="output", size=(65, 15))],
]

credentials_tab_layout = [
    [
        sg.Column(
            [
                [sg.Text("CareFlow username:")],
                [sg.Text("CareFlow password:")],
                [sg.Text("TrakCare username:")],
                [sg.Text("TrakCare password:")],
            ]
        ),
        sg.Column(
            [
                [sg.InputText(key="careflow_username")],
                [sg.InputText(key="careflow_password", password_char="*")],
                [sg.InputText(key="trakcare_username")],
                [sg.InputText(key="trakcare_password", password_char="*")],
            ]
        ),
    ],
    [sg.Button("Set Credentials", key="set_credentials")],
    [
        sg.Text(
            "Note: credentials are never saved to disk, they are held\nin memory "
            "just whilst the program is running."
        )
    ],
]

layout = [
    [
        sg.TabGroup(
            [
                [
                    sg.Tab("Main", main_tab_layout),
                    sg.Tab("Logs", log_tab_layout),
                    sg.Tab("Credentials", credentials_tab_layout),
                ]
            ]
        )
    ]
]

credentials = {
    "careflow_username": "",
    "careflow_password": "",
    "trakcare_username": "",
    "trakcare_password": "",
}

main_window = sg.Window("Patient List Generator", layout)
while True:
    event, values = main_window.read()

    if event is None:
        break

    log_gui(event, values)
    main_window["error_text"].update(visible=False)

    if event == "input_file_path":
        path = Path(values["input_file_path"])
        parent_path = path.parent
        file_ext = path.suffix

        today = datetime.date.today()
        if not values["output_folder_path"]:
            main_window["output_folder_path"].update(parent_path)
            main_window["open_output_folder"].update(disabled=False)

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

    if event == "generate_list_button":
        if values["selected_team"] and values["input_file_path"]:
            team = values["selected_team"]
            input_file_path = Path(values["input_file_path"])
            output_file_path = (
                Path(values["output_folder_path"]) / values["output_filename"]
            )

            main_window["generate_list_button"].update(
                "GENERATING LIST...", disabled=True
            )
            main_window.refresh()

            try:
                pprint(credentials)
                main(
                    team=team,
                    credentials=credentials,
                    input_file_path=input_file_path,
                    output_file_path=output_file_path,
                )

            except Exception as e:
                pprint(e)
                main_window["error_text"].update(visible=True)

            main_window["generate_list_button"].update("Generate List", disabled=False)

    if event == "set_credentials":
        for cred in [
            "careflow_username",
            "careflow_password",
            "trakcare_username",
            "trakcare_password",
        ]:
            credentials[cred] = values[cred].strip()

    if all(
        values[cred]
        for cred in [
            "careflow_username",
            "careflow_password",
            "trakcare_username",
            "trakcare_password",
        ]
    ):
        main_window["set_credentials"].update("Update Credentials")
    else:
        main_window["set_credentials"].update("Set Credentials")

    if values["selected_team"] and not isinstance(values["selected_team"], Team):
        main_window["selected_team"].update(None)

    if values["output_folder_path"]:
        main_window["open_output_folder"].update(disabled=False)

    if values["input_file_path"] and isinstance(values["selected_team"], Team):
        path = Path(values["input_file_path"])
        file_ext = path.suffix
        main_window["output_filename"].update(
            f"{datetime.datetime.today():%d-%m-%Y}_{values['selected_team'].name.value.lower()}{file_ext}"
        )

        main_window["generate_list_button"].update(disabled=False)
