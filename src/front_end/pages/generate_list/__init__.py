import dash_bootstrap_components as dbc
import dash_core_components as dcc

from ..enums import Element as El
from . import components

GENERATE_LIST_LAYOUT = [
    dbc.Row(
        dbc.Col(
            dbc.Card(
                [
                    components.make_team_select_stage(),
                    components.make_upload_previous_list_stage(),
                    dbc.Row(dbc.Col(components.make_generate_list_stage(), width="auto")),
                    dbc.Input(id=El.PREVIOUS_LIST_NAME.value, className="hidden-input", value="",),
                    dcc.Store(id=El.TEMP_UPLOAD_STORE.value, storage_type="memory"),
                ],
                body=True,
            ),
        )
    )
]
