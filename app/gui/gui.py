import datetime
import os
import queue
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import PySimpleGUI as sg

from app.gui.enums import Key, Message
from app.gui.layout import main_layout
from app.gui.utils import log_gui_event, open_folder
from app.main import main
from app.teams import TEAMS, Team

sg.theme("Dark Blue 3")
LOGS_DIR = Path.cwd() / "logs"
LOGS_DIR.mkdir(exist_ok=True)

credentials = {
    Key.CAREFLOW_USERNAME_INPUT: "",
    Key.CAREFLOW_PASSWORD_INPUT: "",
    Key.TRAKCARE_USERNAME_INPUT: "",
    Key.TRAKCARE_PASSWORD_INPUT: "",
}


def _generate_list(queue, values):
    team = values[Key.SELECTED_TEAM]
    input_file_path = Path(values[Key.INPUT_FILE_PATH])
    output_file_path = (
        Path(values[Key.OUTPUT_FOLDER_PATH]) / values[Key.OUTPUT_FILENAME]
    )
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


def run_gui():
    main_window = sg.Window("Patient List Generator", main_layout, finalize=True)

    # switch to the Credentials tab on startup
    main_window[Key.TAB_GROUP].Widget.select(1)
    main_window[Key.CAREFLOW_USERNAME_INPUT].set_focus()
    # bind return key to credential input boxes
    for cred in credentials:
        main_window[cred].bind("<Return>", Key.SET_CREDENTIALS_BUTTON)

    gui_queue = queue.Queue()
    with ThreadPoolExecutor(max_workers=1) as executor:
        while True:
            event, values = main_window.read(timeout=100)

            if event is None:
                break
            elif event != "__TIMEOUT__":
                log_gui_event(event, values)

                main_window[Key.LIST_ERROR_TEXT].update(visible=False)
                main_window[Key.LIST_SUCCESS_TEXT].update(visible=False)
                main_window[Key.CREDENTIALS_SUCCESS_TEXT].update(visible=False)
                main_window[Key.LOGS_SUCCESS_TEXT].update(visible=False)

                if event == Key.INPUT_FILE_PATH:
                    if values[Key.INPUT_FILE_PATH]:
                        path = Path(values[Key.INPUT_FILE_PATH])
                        main_window[Key.INPUT_FILE_PATH].update(path)
                        parent_path = path.parent

                        if not values[Key.OUTPUT_FOLDER_PATH]:
                            main_window[Key.OUTPUT_FOLDER_PATH].update(parent_path)
                            main_window[Key.OPEN_OUTPUT_FOLDER_BUTTON].update(
                                disabled=False
                            )

                if event == Key.OUTPUT_FOLDER_PATH:
                    path = Path(values[Key.OUTPUT_FOLDER_PATH])
                    main_window[Key.OUTPUT_FOLDER_PATH].update(path)

                if event == Key.OPEN_OUTPUT_FOLDER_BUTTON:
                    if not values[Key.OUTPUT_FOLDER_PATH]:
                        continue

                    path = values[Key.OUTPUT_FOLDER_PATH]
                    open_folder(path)

                if event == Key.OPEN_LOGS_FOLDER_BUTTON:
                    open_folder(LOGS_DIR)

                if event == Key.GENERATE_LIST_BUTTON:
                    if values[Key.SELECTED_TEAM] and values[Key.INPUT_FILE_PATH]:
                        executor.submit(_generate_list, gui_queue, values)

                if event == Key.SAVE_LOGS_BUTTON:
                    filename = f"logs_{datetime.datetime.now():%Y-%m-%d_%H_%M_%S}.txt"
                    file_path = LOGS_DIR / filename
                    logs = main_window[Key.OUTPUT_WINDOW].Get()

                    with open(file_path, "w") as fh:
                        fh.writelines(logs)

                    main_window[Key.LOGS_SUCCESS_TEXT].update(
                        f"Logs saved to:\n{file_path}", visible=True
                    )

                # this is a bound event
                if isinstance(event, tuple):
                    if event[1] == Key.SET_CREDENTIALS_BUTTON:
                        for cred in [
                            Key.CAREFLOW_USERNAME_INPUT,
                            Key.CAREFLOW_PASSWORD_INPUT,
                            Key.TRAKCARE_USERNAME_INPUT,
                            Key.TRAKCARE_PASSWORD_INPUT,
                        ]:
                            credentials[cred] = values[cred].strip()
                        main_window[Key.CREDENTIALS_SUCCESS_TEXT].update(visible=True)

                if event == Key.SET_CREDENTIALS_BUTTON:
                    main_window[Key.CREDENTIALS_SUCCESS_TEXT].update(visible=True)


                if all(
                    values[cred]
                    for cred in [
                        Key.CAREFLOW_USERNAME_INPUT,
                        Key.CAREFLOW_PASSWORD_INPUT,
                        Key.TRAKCARE_USERNAME_INPUT,
                        Key.TRAKCARE_PASSWORD_INPUT,
                    ]
                ):
                    main_window[Key.SET_CREDENTIALS_BUTTON].update("Update Credentials")
                else:
                    main_window[Key.SET_CREDENTIALS_BUTTON].update("Set Credentials")

                if values[Key.SELECTED_TEAM] and not isinstance(
                    values[Key.SELECTED_TEAM], Team
                ):
                    main_window[Key.SELECTED_TEAM].update(None)

                if values[Key.OUTPUT_FOLDER_PATH]:
                    main_window[Key.OPEN_OUTPUT_FOLDER_BUTTON].update(disabled=False)

                if values[Key.INPUT_FILE_PATH] and isinstance(
                    values[Key.SELECTED_TEAM], Team
                ):
                    path = Path(values[Key.INPUT_FILE_PATH])
                    file_ext = path.suffix
                    main_window[Key.OUTPUT_FILENAME].update(
                        f"{datetime.datetime.today():%d-%m-%Y}_"
                        f"{values[Key.SELECTED_TEAM].name.value.lower()}{file_ext}"
                    )

                    main_window[Key.GENERATE_LIST_BUTTON].update(disabled=False)

            try:
                message = gui_queue.get_nowait()
            except queue.Empty:
                pass
            else:
                if message == Message.START_GENERATING_LIST:
                    main_window[Key.GENERATE_LIST_BUTTON].update(
                        "GENERATING LIST...", disabled=True
                    )

                if message == Message.ERROR_GENERATING_LIST:
                    main_window[Key.GENERATE_LIST_BUTTON].update(
                        "Generate List", disabled=False
                    )
                    main_window[Key.LIST_SUCCESS_TEXT].update(visible=True)

                if message == Message.FINISH_GENERATING_LIST:
                    main_window[Key.GENERATE_LIST_BUTTON].update(
                        "Generate List", disabled=False
                    )
                    main_window[Key.LIST_ERROR_TEXT].update(visible=True)
