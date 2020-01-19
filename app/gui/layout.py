import PySimpleGUI as sg

from app.gui.enums import Key
from app.teams import TEAMS

main_tab_layout = [
    [sg.Text("Choose input file:*")],
    [
        sg.InputText(
            size=(55, 1), disabled=True, key=Key.INPUT_FILE_PATH, enable_events=True
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
            key=Key.SELECTED_TEAM,
        )
    ],
    [sg.Text("Output folder:")],
    [
        sg.InputText(
            size=(55, 1), disabled=True, key=Key.OUTPUT_FOLDER_PATH, enable_events=True
        ),
        sg.FolderBrowse(),
    ],
    [sg.Text("Output filename:")],
    [sg.InputText(disabled=True, key=Key.OUTPUT_FILENAME)],
    [
        sg.Button("Generate List", key=Key.GENERATE_LIST_BUTTON, disabled=True,),
        sg.Button(
            "Open Output Folder", key=Key.OPEN_OUTPUT_FOLDER_BUTTON, disabled=True
        ),
    ],
    [
        sg.Text(
            " Error - please check the logs",
            key=Key.LIST_ERROR_TEXT,
            visible=False,
            font=("Helvetica", 12, "bold"),
        )
    ],
    [
        sg.Text(
            " List generated successfully",
            key=Key.LIST_SUCCESS_TEXT,
            font=("Helvetica", 11),
            visible=False,
        )
    ],
]

log_tab_layout = [
    [sg.Output(key=Key.OUTPUT_WINDOW, size=(65, 15))],
    [
        sg.Button("Save", key=Key.SAVE_LOGS_BUTTON),
        sg.Button("Open Logs", key=Key.OPEN_LOGS_FOLDER_BUTTON),
    ],
    [
        sg.Text(
            "Logs saved successfully",
            key=Key.LOGS_SUCCESS_TEXT,
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
                [sg.InputText(key=Key.CAREFLOW_USERNAME_INPUT)],
                [sg.InputText(key=Key.CAREFLOW_PASSWORD_INPUT, password_char="*")],
                [sg.InputText(key=Key.TRAKCARE_USERNAME_INPUT)],
                [sg.InputText(key=Key.TRAKCARE_PASSWORD_INPUT, password_char="*")],
            ]
        ),
    ],
    [sg.Button("Set Credentials", key=Key.SET_CREDENTIALS_BUTTON)],
    [
        sg.Text(
            " Credentials set successfully",
            key=Key.CREDENTIALS_SUCCESS_TEXT,
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

main_layout = [
    [
        sg.TabGroup(
            [
                [
                    sg.Tab("Main", main_tab_layout),
                    sg.Tab("Credentials", credentials_tab_layout),
                    sg.Tab("Logs", log_tab_layout),
                ]
            ],
            key=Key.TAB_GROUP,
        )
    ]
]
