from enum import Enum


class Element(Enum):
    # navigation tabs
    NAV_TABS = "nav-tabs"
    GENERATE_LIST_TAB = "generate-list-tab"

    # page content
    PAGE_CONTENT = "page-content"

    # main tab
    SELECT_TEAM_INPUT = "select-team-input"
    UPLOAD_PREVIOUS_LIST_BUTTON = "upload-previous-list-button"
    DETECTED_FILE_TEXT = "chosen-file-text"
    UPLOADED_FILE_TEXT = "uploaded-file-text"
    DELETE_UPLOADED_FILE_BUTTON = "delete-uploaded-file-button"
    GENERATE_LIST_BUTTON = "generate-list-button"
    PREVIOUS_LIST_NAME = "previous-list-detected-name"
    LIST_GENERATION_STATUS = "list-generation-status"
    TEMP_UPLOAD_STORE = "temp-upload-store"
