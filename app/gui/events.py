import datetime
from pathlib import Path

from app.gui import credential_keys
from app.gui.enums import Key
from app.gui.utils import generate_list, open_folder

LOGS_DIR = Path.cwd() / "logs"


def handle_input_file_path(values, window, gui_queue, executor):
    if values[Key.INPUT_FILE_PATH]:
        path = Path(values[Key.INPUT_FILE_PATH])
        window[Key.INPUT_FILE_PATH].update(path)
        parent_path = path.parent

        if not values[Key.OUTPUT_FOLDER_PATH]:
            window[Key.OUTPUT_FOLDER_PATH].update(parent_path)
            window[Key.OPEN_OUTPUT_FOLDER_BUTTON].update(disabled=False)


def handle_output_folder_path(values, window, gui_queue, executor):
    path = Path(values[Key.OUTPUT_FOLDER_PATH])
    window[Key.OUTPUT_FOLDER_PATH].update(path)


def handle_open_output_folder_button(values, window, gui_queue, executor):
    if not values[Key.OUTPUT_FOLDER_PATH]:
        return

    path = values[Key.OUTPUT_FOLDER_PATH]
    open_folder(path)


def handle_open_logs_folder_button(values, window, gui_queue, executor):
    open_folder(LOGS_DIR)


def handle_generate_list_button(values, window, gui_queue, executor):
    if values[Key.SELECTED_TEAM] and values[Key.INPUT_FILE_PATH]:
        executor.submit(generate_list, gui_queue, values)


def handle_save_logs_button(values, window, gui_queue, executor):
    filename = f"logs_{datetime.datetime.now():%Y-%m-%d_%H_%M_%S}.txt"
    file_path = LOGS_DIR / filename
    logs = window[Key.OUTPUT_WINDOW].Get()

    with open(file_path, "w") as fh:
        fh.writelines(logs)

    window[Key.LOGS_SUCCESS_TEXT].update(f"Logs saved to:\n{file_path}", visible=True)


def handle_set_credentials_button(values, window, gui_queue, executor):
    for cred in credential_keys:
        window[cred].update(values[cred].strip())
    window[Key.CREDENTIALS_SUCCESS_TEXT].update(visible=True)


def handle_selected_team(values, window, gui_queue, executor):
    pass


EVENTS = {
    Key.INPUT_FILE_PATH: handle_input_file_path,
    Key.OUTPUT_FOLDER_PATH: handle_output_folder_path,
    Key.OPEN_OUTPUT_FOLDER_BUTTON: handle_open_output_folder_button,
    Key.OPEN_LOGS_FOLDER_BUTTON: handle_open_logs_folder_button,
    Key.GENERATE_LIST_BUTTON: handle_generate_list_button,
    Key.SAVE_LOGS_BUTTON: handle_save_logs_button,
    Key.SET_CREDENTIALS_BUTTON: handle_set_credentials_button,
    Key.SELECTED_TEAM: handle_selected_team,
}
