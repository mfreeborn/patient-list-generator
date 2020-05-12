import datetime
import logging
import os
import queue
import subprocess
import time
from pathlib import Path

import PySimpleGUI as sg

from app.gui.enums import Key, Message
from app.main import main
from app.teams import Team
from app.utils import formatter

logger = logging.getLogger("PLG")


def generate_list(queue, values):
    team = values[Key.SELECTED_TEAM]
    input_file_path = Path(values[Key.INPUT_FILE_PATH])
    output_file_path = Path(values[Key.OUTPUT_FOLDER_PATH]) / values[Key.OUTPUT_FILENAME]

    queue.put(Message.START_GENERATING_LIST)
    # this sleep gives just enough time for the context to switch back to the main gui thread,
    # allowing it to update the gui in response to the sent message more responsively.
    time.sleep(0.01)
    try:
        main(
            team=team, input_file_path=input_file_path, output_file_path=output_file_path,
        )
    except Exception as e:
        queue.put(Message.ERROR_GENERATING_LIST)
        logger.exception(e)
    else:
        queue.put(Message.FINISH_GENERATING_LIST)


def init_gui(window_title, layout, theme=None):
    """Helper function for initialising the gui."""
    logging.debug("Initialising GUI")
    if theme is None:
        theme = "Dark Blue 3"
    sg.theme(theme)

    main_window = sg.Window(window_title, layout, finalize=True)

    # configure logging output to go to the Output element
    tk_streamhandler = logging.StreamHandler(main_window[Key.OUTPUT_WINDOW].TKOut)
    tk_streamhandler.setFormatter(formatter)
    logger.addHandler(tk_streamhandler)

    return main_window, queue.Queue()


def log_gui_event(event: str, values: dict):
    """Helper function for logging events in the gui."""
    # make a copy of the values dict so we don't overwrite anything permanently
    values = dict(values)
    values = {key.value: value for key, value in values.items() if isinstance(key, Key)}

    logger.debug(
        "Event '%s' received with the values:\n\t{%s}",
        event,
        "\n\t".join(f"{key!r}: {value!r}" for key, value in values.items()),
    )


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
    window[Key.LOGS_SUCCESS_TEXT].update(visible=False)


def update_gui(values, window):
    """Handle the state of the gui depending on what values are/are not present."""
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

        if window[Key.GENERATE_LIST_BUTTON].get_text().lower() != "generating list...":
            window[Key.GENERATE_LIST_BUTTON].update(disabled=False)
