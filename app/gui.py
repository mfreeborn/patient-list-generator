import datetime
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import queue

import PySimpleGUI as sg

from app.main import main
from app.teams import TEAMS, Team
from app.utils import log_gui

sg.theme("Dark Blue 3")
LOGS_DIR = Path.cwd() / "logs"
LOGS_DIR.mkdir(exist_ok=True)

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
            " Error - please check the logs",
            key="error_text",
            visible=False,
            font=("Helvetica", 12, "bold"),
        )
    ],
    [
        sg.Text(
            " List generated successfully",
            key="list_success_text",
            font=("Helvetica", 11),
            visible=False,
        )
    ],
]

log_tab_layout = [
    [sg.Output(key="output", size=(65, 15))],
    [
        sg.Button("Save", key="save_logs_button"),
        sg.Button("Open Logs", key="open_logs_folder"),
    ],
    [
        sg.Text(
            "Logs saved successfully",
            key="logs_success_text",
            font=("Helvetica", 10),
            size=(65, 2),
            visible=False,
        )
    ],
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
            " Credentials set successfully",
            key="credentials_success_text",
            font=("Helvetica", 11),
            visible=False,
        ),
    ],
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
                    sg.Tab("Credentials", credentials_tab_layout),
                    sg.Tab("Logs", log_tab_layout),
                ]
            ],
            key="tab_group",
        )
    ]
]

credentials = {
    "careflow_username": "",
    "careflow_password": "",
    "trakcare_username": "",
    "trakcare_password": "",
}


def open_folder(path: str):
    if os.name == "nt":
        # Windows
        os.startfile(path)
    else:
        # Linux
        subprocess.Popen(["xdg-open", path])


def _generate_list(queue, values):
    team = values["selected_team"]
    input_file_path = Path(values["input_file_path"])
    output_file_path = Path(values["output_folder_path"]) / values["output_filename"]
    queue.put("start_generating_list")
    try:
        main(
            team=team,
            credentials=credentials,
            input_file_path=input_file_path,
            output_file_path=output_file_path,
        )

    except Exception as e:
        print(e)
        queue.put("error_generating_list")
    else:
        queue.put("finish_generating_list")


def run_gui():
    main_window = sg.Window("Patient List Generator", layout, finalize=True)

    # switch to the Credentials tab on startup
    main_window["tab_group"].Widget.select(1)
    main_window["careflow_username"].set_focus()
    # bind return key to credential input boxes
    for cred in credentials:
        main_window[cred].bind("<Return>", "set_credentials")

    gui_queue = queue.Queue()
    with ThreadPoolExecutor(max_workers=1) as executor:
        while True:
            event, values = main_window.read(timeout=100)

            if event is None:
                break
            elif event != "__TIMEOUT__":
                log_gui(event, values)

                main_window["error_text"].update(visible=False)
                main_window["list_success_text"].update(visible=False)
                main_window["credentials_success_text"].update(visible=False)
                main_window["logs_success_text"].update(visible=False)

                if event == "input_file_path":
                    if values["input_file_path"]:
                        path = Path(values["input_file_path"])
                        main_window['input_file_path'].update(path)
                        parent_path = path.parent

                        if not values["output_folder_path"]:
                            main_window["output_folder_path"].update(parent_path)
                            main_window["open_output_folder"].update(disabled=False)

                if event == "open_output_folder":
                    if not values["output_folder_path"]:
                        continue

                    path = values["output_folder_path"]
                    open_folder(path)

                if event == "open_logs_folder":
                    open_folder(LOGS_DIR)

                if event == "generate_list_button":
                    if values["selected_team"] and values["input_file_path"]:
                        executor.submit(_generate_list, gui_queue, values)

                if event == "save_logs_button":
                    filename = f"logs_{datetime.datetime.now():%Y-%m-%d_%H_%M_%S}.txt"
                    file_path = LOGS_DIR / filename
                    logs = main_window["output"].Get()

                    with open(file_path, "w") as fh:
                        fh.writelines(logs)

                    main_window["logs_success_text"].update(
                        f"Logs saved to:\n{file_path}", visible=True
                    )

                if event.endswith("set_credentials"):
                    for cred in [
                        "careflow_username",
                        "careflow_password",
                        "trakcare_username",
                        "trakcare_password",
                    ]:
                        credentials[cred] = values[cred].strip()
                    main_window["credentials_success_text"].update(visible=True)

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

                if values["selected_team"] and not isinstance(
                    values["selected_team"], Team
                ):
                    main_window["selected_team"].update(None)

                if values["output_folder_path"]:
                    main_window["open_output_folder"].update(disabled=False)

                if values["input_file_path"] and isinstance(
                    values["selected_team"], Team
                ):
                    path = Path(values["input_file_path"])
                    file_ext = path.suffix
                    main_window["output_filename"].update(
                        f"{datetime.datetime.today():%d-%m-%Y}_"
                        f"{values['selected_team'].name.value.lower()}{file_ext}"
                    )

                    main_window["generate_list_button"].update(disabled=False)

            try:
                message = gui_queue.get_nowait()
            except queue.Empty:
                pass
            else:
                if message == "start_generating_list":
                    main_window["generate_list_button"].update(
                        "GENERATING LIST...", disabled=True
                    )

                if message == "finish_generating_list":
                    main_window["generate_list_button"].update(
                        "Generate List", disabled=False
                    )
                    main_window["list_success_text"].update(visible=True)

                if message == "error_generating_list":
                    main_window["generate_list_button"].update(
                        "Generate List", disabled=False
                    )
                    main_window["error_text"].update(visible=True)
