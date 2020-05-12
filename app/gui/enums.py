from enum import Enum, unique


@unique
class Key(Enum):
    """Enumerations for each gui component key."""

    GENERATE_LIST_BUTTON = "generate_list_button"
    INPUT_FILE_PATH = "input_file_path"
    LIST_ERROR_TEXT = "list_error_text"
    LIST_SUCCESS_TEXT = "list_success_text"
    LOGS_SUCCESS_TEXT = "logs_success_text"
    OPEN_LOGS_FOLDER_BUTTON = "open_logs_folder_button"
    OPEN_OUTPUT_FOLDER_BUTTON = "open_output_folder_button"
    OUTPUT_FILENAME = "output_filename"
    OUTPUT_FOLDER_PATH = "output_folder_path"
    OUTPUT_WINDOW = "output_window"
    SAVE_LOGS_BUTTON = "save_logs_button"
    SELECTED_TEAM = "selected_team"
    TAB_GROUP = "tab_group"


@unique
class Message(Enum):
    """Enumerations for inter-thread messaging."""

    START_GENERATING_LIST = "start_generating_list"
    FINISH_GENERATING_LIST = "finish_generating_list"
    ERROR_GENERATING_LIST = "error_generating_list"
