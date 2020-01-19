import datetime
import os
import queue
import subprocess
from pathlib import Path
from pprint import pprint

import PySimpleGUI as sg

from app.gui import credential_keys
from app.gui.enums import Key, Message
from app.main import main
from app.teams import Team


def generate_list(queue, values):
    team = values[Key.SELECTED_TEAM]
    input_file_path = Path(values[Key.INPUT_FILE_PATH])
    output_file_path = (
        Path(values[Key.OUTPUT_FOLDER_PATH]) / values[Key.OUTPUT_FILENAME]
    )

    credentials = {cred: values[cred] for cred in credential_keys}

    queue.put(Message.START_GENERATING_LIST)

    try:
        main(
            team=team,
            credentials=credentials,
            input_file_path=input_file_path,
            output_file_path=output_file_path,
        )
    except Exception as e:
        print(e)
        queue.put(Message.ERROR_GENERATING_LIST)
        raise
    else:
        queue.put(Message.FINISH_GENERATING_LIST)


def init_gui(window_title, layout, theme=None):
    """Helper function for initialising the gui."""
    if theme is None:
        theme = "Dark Blue 3"
    sg.theme(theme)

    main_window = sg.Window(window_title, layout, finalize=True)

    # switch to the Credentials tab on startup
    main_window[Key.TAB_GROUP].Widget.select(1)
    main_window[Key.CAREFLOW_USERNAME_INPUT].set_focus()

    # bind return key to credential input boxes
    for cred in credential_keys:
        main_window[cred].bind("<Return>", Key.SET_CREDENTIALS_BUTTON)

    return main_window, queue.Queue()


def log_gui_event(event: str, values: dict):
    """Helper function for logging events in the gui.

    Specifically conceals sensitive information before printing."""
    # make a copy of the values dict so we don't overwrite anything permanently
    values = dict(values)
    values[Key.CAREFLOW_PASSWORD_INPUT] = (
        "*" * 5 if values[Key.CAREFLOW_PASSWORD_INPUT] else ""
    )
    values[Key.TRAKCARE_PASSWORD_INPUT] = (
        "*" * 5 if values[Key.TRAKCARE_PASSWORD_INPUT] else ""
    )

    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
    print()
    print(event)
    pprint(values)
    print()
    print("-" * 30)
    print()


def open_folder(path: str):
    if os.name == "nt":
        # Windows
        os.startfile(path)
    else:
        # Linux
        subprocess.Popen(["xdg-open", path])


def set_text_invisible(window):
    """Set user feedback messages to non-visible."""
    window[Key.LIST_ERROR_TEXT].update(visible=False)
    window[Key.LIST_SUCCESS_TEXT].update(visible=False)
    window[Key.CREDENTIALS_SUCCESS_TEXT].update(visible=False)
    window[Key.LOGS_SUCCESS_TEXT].update(visible=False)


def update_gui(values, window):
    """Handle the state of the gui depending on what values are/are not present."""
    if all(values[cred] for cred in credential_keys):
        window[Key.SET_CREDENTIALS_BUTTON].update("Update Credentials")
    else:
        window[Key.SET_CREDENTIALS_BUTTON].update("Set Credentials")

    if values[Key.SELECTED_TEAM] and not isinstance(values[Key.SELECTED_TEAM], Team):
        window[Key.SELECTED_TEAM].update(None)

    if values[Key.OUTPUT_FOLDER_PATH]:
        window[Key.OPEN_OUTPUT_FOLDER_BUTTON].update(disabled=False)

    if values[Key.INPUT_FILE_PATH] and isinstance(values[Key.SELECTED_TEAM], Team):
        path = Path(values[Key.INPUT_FILE_PATH])
        file_ext = path.suffix
        window[Key.OUTPUT_FILENAME].update(
            f"{datetime.datetime.today():%d-%m-%Y}_"
            f"{values[Key.SELECTED_TEAM].name.value.lower()}{file_ext}"
        )

        window[Key.GENERATE_LIST_BUTTON].update(disabled=False)
