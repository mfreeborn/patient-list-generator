import datetime
import queue
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.gui import credential_keys
from app.gui.enums import Key, Message
from app.gui.events import EVENTS
from app.gui.layout import main_layout
from app.gui.utils import init_gui, log_gui_event, set_text_invisible
from app.teams import Team

LOGS_DIR = Path.cwd() / "logs"
LOGS_DIR.mkdir(exist_ok=True)


def run_gui():
    main_window = init_gui(window_title="Patient List Generator", layout=main_layout)

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

                if all(values[cred] for cred in credential_keys):
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
