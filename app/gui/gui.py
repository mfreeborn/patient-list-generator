import datetime
import queue
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import PySimpleGUI as sg

from app.gui.enums import Key, Message
from app.gui.events import EVENTS
from app.gui.layout import main_layout
from app.gui.utils import log_gui_event, set_text_invisible
from app.teams import Team

sg.theme("Dark Blue 3")
LOGS_DIR = Path.cwd() / "logs"
LOGS_DIR.mkdir(exist_ok=True)

credentials = {
    Key.CAREFLOW_USERNAME_INPUT: "",
    Key.CAREFLOW_PASSWORD_INPUT: "",
    Key.TRAKCARE_USERNAME_INPUT: "",
    Key.TRAKCARE_PASSWORD_INPUT: "",
}


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
                # closes the program
                break

            elif event != "__TIMEOUT__":
                # handles any user events (i.e. not just a timeout)
                log_gui_event(event, values)
                set_text_invisible(window=main_window)

                # this is a bound event
                if isinstance(event, tuple):
                    event = event[1]

                EVENTS[event](values, main_window, gui_queue, executor)

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
                    main_window[Key.LIST_ERROR_TEXT].update(visible=True)

                if message == Message.FINISH_GENERATING_LIST:
                    main_window[Key.GENERATE_LIST_BUTTON].update(
                        "Generate List", disabled=False
                    )
                    main_window[Key.LIST_SUCCESS_TEXT].update(visible=True)
