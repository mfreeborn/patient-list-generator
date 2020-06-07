import base64
import datetime
import io
import logging
from pathlib import Path

import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from .. import settings, utils
from ..list_generator import generate_list
from ..shared_enums import Team
from .app import app
from .layouts import pages
from .layouts.enums import Element as El

logger = logging.getLogger()


@app.callback(Output(El.PAGE_CONTENT.value, "children"), [Input(El.NAV_TABS.value, "active_tab")])
@utils.log_callback
def switch_tab(active_tab):
    """Handle loading the page-content div with the correct contents according to the nav tabs."""
    selected_tab = El(active_tab)

    if selected_tab == El.GENERATE_LIST_TAB:
        app.logger.debug("Creating the List Generation page")
        return pages.GENERATE_LIST_LAYOUT


@app.callback(
    Output(El.UPLOAD_PREVIOUS_LIST_BUTTON.value, "disabled"),
    [Input(El.SELECT_TEAM_INPUT.value, "value")],
)
@utils.log_callback
def initialise_file_upload_stage(selected_team):
    """Handle enabling the upload button in the second stage, once the first stage is complete."""
    if selected_team is None:
        # this happens on initial page load
        raise PreventUpdate
    return False


@app.callback(
    [
        Output(El.DETECTED_FILE_TEXT.value, "children"),
        Output(El.PREVIOUS_LIST_NAME.value, "value"),
    ],
    [Input(El.SELECT_TEAM_INPUT.value, "value")],
)
@utils.log_callback
def locate_previous_list(selected_team):
    """Attempt to locate the most recent handover list to save the user manually uploading it."""
    if selected_team is None:
        # this happens on initial page load
        raise PreventUpdate

    team = Team.from_team_name(selected_team)

    # try and find the most recent handover list automatically. Do this by searching back up to
    # a week ago for a handover list identified by a specific filename format
    team_list_dir = settings.LIST_ROOT_DIR / f"{team.name}"
    today = datetime.date.today()
    for n_days in range(1, 7):
        previous_day = today - datetime.timedelta(days=n_days)
        current_team_list_dir = team_list_dir / f"{previous_day.year}" / f"{previous_day:%m %B}"

        # make the folder first if it doesn't exist
        current_team_list_dir.mkdir(parents=True, exist_ok=True)

        previous_handover_list = None
        for file in current_team_list_dir.iterdir():
            if file.stem == f"{previous_day:%d-%m-%Y}_{team.name}".lower():
                previous_handover_list = file

        if previous_handover_list is not None:
            # we've found the most recent handover list, so exit the loop
            break
    else:
        # no previous handover list was found
        previous_handover_list = None

    if previous_handover_list is None:
        return html.P("No previous list detected; upload your own below"), ""

    list_found_text = [
        html.P("Recent handover list detected:", className="no-bottom-margin"),
        html.P(
            [html.Pre("\t"), html.P(previous_handover_list.name)],
            className="inline-p no-bottom-margin",
        ),
        html.P(
            ["Continue to step 3 ", html.Span("or", className="italic"), " upload your own below"]
        ),
    ]

    return list_found_text, previous_handover_list.name


@app.callback(
    Output(El.GENERATE_LIST_BUTTON.value, "disabled"),
    [Input(El.PREVIOUS_LIST_NAME.value, "value"), Input(El.TEMP_UPLOAD_STORE.value, "data")],
    [State(El.GENERATE_LIST_BUTTON.value, "disabled")],
)
@utils.log_callback
def initialise_generate_list_stage(prev_list_name, uploaded_file_data, previous_disabled_state):
    """Set the disabled attribute of the Generate List button depending on the state of the form."""
    trigger = utils.parse_trigger(dash.callback_context)
    if not trigger:
        raise PreventUpdate

    new_disabled_state = True

    # enable the Generate List button either if we have found a previous handover list
    # or if the user has uploaded a list
    if prev_list_name or uploaded_file_data:
        new_disabled_state = False

    return new_disabled_state


@app.callback(
    Output(El.UPLOAD_PREVIOUS_LIST_BUTTON.value, "contents"),
    [Input(El.DELETE_UPLOADED_FILE_BUTTON.value, "n_clicks")],
)
@utils.log_callback
def clear_upload_contents(n_clicks):
    """Handle emptying the contents of the Upload button."""
    if n_clicks is None:
        raise PreventUpdate
    return ""


@app.callback(
    Output(El.TEMP_UPLOAD_STORE.value, "data"),
    [
        Input(El.UPLOAD_PREVIOUS_LIST_BUTTON.value, "contents"),
        Input(El.DELETE_UPLOADED_FILE_BUTTON.value, "n_clicks"),
    ],
    [State(El.UPLOAD_PREVIOUS_LIST_BUTTON.value, "filename")],
)
@utils.log_callback
def handle_list_upload(file_contents, n_clicks, filename):
    """Parse the contents of the Upload button and save it to the Store."""
    trigger = utils.parse_trigger(dash.callback_context)
    if not trigger:
        raise PreventUpdate

    if trigger == El.UPLOAD_PREVIOUS_LIST_BUTTON:
        # get the file contents as a base64 encoded string and store it
        _, content_string = file_contents.split(",")

        return {"contents": content_string, "filename": filename}
    else:
        # the trigger is the delete button, so set the store to be empty
        return {}


@app.callback(
    [
        Output(El.UPLOADED_FILE_TEXT.value, "children"),
        Output(El.DELETE_UPLOADED_FILE_BUTTON.value, "style"),
    ],
    [
        Input(El.TEMP_UPLOAD_STORE.value, "data"),
        Input(El.DELETE_UPLOADED_FILE_BUTTON.value, "n_clicks"),
    ],
)
@utils.log_callback
def set_uploaded_file_info(uploaded_file_data, n_clicks):
    """Handle displaying information about the uplaoded file."""
    trigger = utils.parse_trigger(dash.callback_context)
    if not trigger:
        raise PreventUpdate

    if trigger == El.TEMP_UPLOAD_STORE:
        # a file was just uploaded, so display the filename to the user
        return uploaded_file_data["filename"], {"display": "inline-block"}
    else:
        # otherwise the trigger was the delete button, so remove the previous filename
        return "", {"display": "none"}


@app.callback(
    Output(El.LIST_GENERATION_STATUS.value, "children"),
    [
        Input(El.GENERATE_LIST_BUTTON.value, "n_clicks"),
        Input(El.SELECT_TEAM_INPUT.value, "value"),
        Input(El.TEMP_UPLOAD_STORE.value, "data"),
    ],
    [State(El.PREVIOUS_LIST_NAME.value, "value")],
)
@utils.log_callback
def handle_generate_list(n_clicks, selected_team, uploaded_file_data, detected_list_filename):
    """Handle passing the contents of the list generator function."""
    trigger = utils.parse_trigger(dash.callback_context)
    if not trigger:
        raise PreventUpdate

    if trigger in {El.SELECT_TEAM_INPUT, El.TEMP_UPLOAD_STORE}:
        # clear the status
        return None

    team = Team.from_team_name(selected_team)

    if uploaded_file_data:
        # use the uploaded list if one has been provided, otherwise use the auto-detected list
        app.logger.info("Will use the uploaded file as a base for the updated handover list")
        file_io = io.BytesIO(base64.b64decode(uploaded_file_data["contents"]))
        filename = Path(uploaded_file_data["filename"])
    else:
        # otherwise fallback to the auto-detected file
        app.logger.info("Will use the auto-detected file as a base for the updated handoiver list")
        filename = Path(detected_list_filename)
        list_date = datetime.datetime.strptime(detected_list_filename.split("_")[0], "%d-%m-%Y")
        input_file_path = (
            settings.LIST_ROOT_DIR
            / f"{team.name}"
            / f"{list_date:%Y}"
            / f"{list_date:%m %B}"
            / filename
        )
        with open(input_file_path, "rb") as fh:
            file_io = io.BytesIO(fh.read())

    try:
        output_file_path = generate_list(team, file_io, filename)
    except Exception as e:
        app.logger.exception(e)
        return f"List generation failed due to the following error: '{e}'"

    return f"List generated succesfully. Saved at {output_file_path}"
