import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from .....shared_enums import Team
from ...enums import Element as El


def make_team_select_stage():
    select_options = [
        {"label": team.value.name.value, "value": team.value.name.value} for team in Team
    ]

    return html.Div(
        [
            html.P("1. Select a team", className="form-label"),
            dbc.Select(
                id=El.SELECT_TEAM_INPUT.value,
                className="select-team-input stage-content",
                options=select_options,
                value=None,
            ),
        ],
        className="form-stage-div",
    )


def make_upload_previous_list_stage():
    return html.Div(
        [
            html.P("2. Choose an input list", className="form-label"),
            html.Div(
                [
                    html.Div(id=El.DETECTED_FILE_TEXT.value),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Upload(
                                    dbc.Button("Upload"),
                                    id=El.UPLOAD_PREVIOUS_LIST_BUTTON.value,
                                    accept=(
                                        ".doc,.docx,.docm,application/msword,application/"
                                        "vnd.openxmlformats-officedocument.wordprocessingml"
                                        ".document"
                                    ),
                                    disabled=True,
                                ),
                                width="auto",
                            ),
                            dbc.Col(html.Div(id=El.UPLOADED_FILE_TEXT.value), width="auto"),
                            dbc.Col(
                                dbc.Button(
                                    "X",
                                    id=El.DELETE_UPLOADED_FILE_BUTTON.value,
                                    className="delete-uploaded-file-button",
                                    style={"display": "none"},
                                )
                            ),
                        ],
                        style={"alignItems": "center"},
                    ),
                ],
                className="stage-content",
            ),
        ],
        className="form-stage-div",
    )


def make_generate_list_stage():
    return html.Div(
        [
            html.P("3. Generate a new list", className="form-label"),
            html.Div(
                dcc.Loading(
                    html.Div(
                        [
                            dbc.Button(
                                "Generate List", id=El.GENERATE_LIST_BUTTON.value, disabled=True
                            ),
                            html.P(
                                id=El.LIST_GENERATION_STATUS.value, className="status-text-output"
                            ),
                        ],
                    ),
                    style={"marginLeft": -85, "visbility": "visible"},
                    type="default",
                ),
                className="stage-content",
            ),
        ]
    )
