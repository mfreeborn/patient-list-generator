import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from .enums import Element as El


def BASE_LAYOUT():
    return html.Div(
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                dcc.Graph(id=El.PATIENTS_PER_TEAM_GRAPH.value),
                                id=El.PATIENTS_PER_TEAM_CARD.value,
                                body=False,
                            )
                        ),
                        dbc.Col(dbc.Card("row1 col2", body=True)),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(dbc.Card("row2 col1", body=True)),
                        dbc.Col(dbc.Input(id="test-input", value="yo")),
                    ]
                ),
            ],
            id=El.PAGE_CONTENT.value,
        )
    )
