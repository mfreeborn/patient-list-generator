import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from . import charts
from .app import app
from .layouts.enums import Element as El


@app.callback(Output(El.PATIENTS_PER_TEAM_GRAPH.value, "figure"), [Input("test-input", "value")])
def load_patient_per_team_card(value):
    return charts.patients_per_team_chart()
