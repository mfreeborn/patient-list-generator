import datetime
import os
import subprocess
from pprint import pprint
from app.gui.enums import Key
from pathlib import Path

def generate_list(queue, values):
    print('hi')
    team = values[Key.SELECTED_TEAM]
    print(team)
    try:
        input_file_path = Path(values[Key.INPUT_FILE_PATH])
    except Exception as e:
        print(exception)
    print(input_file_path)
    output_file_path = (
        Path(values[Key.OUTPUT_FOLDER_PATH]) / values[Key.OUTPUT_FILENAME]
    )
    print(output_file_path)
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
        queue.put(Message.FINISH_GENERATING_LIST)
    else:
        queue.put(Message.ERROR_GENERATING_LIST)


def log_gui_event(event: str, values: dict):
    """Helper function for logging events in the gui.

    Specifically conceals sensitive information before printing."""
    # make a copy of the values dict so we don't overwrite anything permanently
    values = dict(values)
    values[Key.CAREFLOW_PASSWORD_INPUT] = "*" * 5 if values[Key.CAREFLOW_PASSWORD_INPUT] else ""
    values[Key.TRAKCARE_PASSWORD_INPUT] = "*" * 5 if values[Key.TRAKCARE_PASSWORD_INPUT] else ""

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
