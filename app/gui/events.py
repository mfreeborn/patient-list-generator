import datetime
import logging
from pathlib import Path

from app.enums import TeamName
from app.gui import LOGS_DIR
from app.gui.enums import Key
from app.gui.utils import generate_list, open_folder
from app.teams import TEAMS

logger = logging.getLogger("PLG")


def handle_input_file_path(values, window, gui_queue, executor):
    if values[Key.INPUT_FILE_PATH]:
        path = Path(values[Key.INPUT_FILE_PATH])
        window[Key.INPUT_FILE_PATH].update(path)

        # see if we can parse out the name of the team to set the
        # selected_team element as a convenience
        filename = path.stem
        file_ext = path.suffix
        team_name = filename.split("_")[-1].capitalize()

        try:
            team = TEAMS[TeamName(team_name)]
        except ValueError:
            pass
        else:
            window[Key.SELECTED_TEAM].update(team)
            window[Key.OUTPUT_FILENAME].update(
                f"{datetime.datetime.today():%d-%m-%Y}_" f"{team.name.value.lower()}{file_ext}"
            )
            window[Key.GENERATE_LIST_BUTTON].update(disabled=False)

        if not values[Key.OUTPUT_FOLDER_PATH]:
            parent_path = path.parent
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

    logger.debug("Logs saved to %s", file_path)
    window[Key.LOGS_SUCCESS_TEXT].update(f"Logs saved to:\n{file_path}", visible=True)


def handle_selected_team(values, window, gui_queue, executor):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    team_name = values[Key.SELECTED_TEAM].name.value

    base_directory = Path("H:\\") / "Medicine" / "Handover Lists" / team_name

    yesterdays_directory = base_directory / f"{yesterday:%Y}" / f"{yesterday:%d %B}"
    todays_directory = base_directory / f"{today:%Y}" / f"{today:%d %B}"

    default_filename = f"{today:%d-%m-%Y}_{team_name.lower()}.docx"
    todays_filepath = todays_directory / default_filename

    if yesterdays_directory.is_dir():
        previous_lists = sorted(
            file
            for file in yesterdays_directory.iterdir()
            if file.is_file() and file.suffix.lower() in {".docx", ".docm"}
        )

        if previous_lists:
            # if we find any good looking files, get the most recent list and use that file
            # extension as the basis for the today's file
            previous_list = previous_lists[-1]
            file_extension = previous_list.suffix.lower()
            todays_filepath = todays_filepath.with_sufix(file_extension)

            if not values[Key.INPUT_FILE_PATH]:
                window[Key.INPUT_FILE_PATH].update(previous_list)

    window[Key.OUTPUT_FOLDER_PATH].update(todays_directory)

    window[Key.OUTPUT_FILENAME].update(todays_filepath.name)


def no_op(values, window, gui_queue, executor):
    pass


EVENTS = {
    Key.INPUT_FILE_PATH: handle_input_file_path,
    Key.OUTPUT_FOLDER_PATH: handle_output_folder_path,
    Key.OPEN_OUTPUT_FOLDER_BUTTON: handle_open_output_folder_button,
    Key.OPEN_LOGS_FOLDER_BUTTON: handle_open_logs_folder_button,
    Key.GENERATE_LIST_BUTTON: handle_generate_list_button,
    Key.SAVE_LOGS_BUTTON: handle_save_logs_button,
    Key.SELECTED_TEAM: handle_selected_team,
}
