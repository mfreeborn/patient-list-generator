import plotly.graph_objects as go

from .app import db
from .models import Inpatient


def patients_per_team_chart():
    pts = db.session.query(Inpatient).all()
    print("hi")
    print(pts)
    fig = go.Figure(
        data=[
            {"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar", "name": "SF"},
            {"x": [1, 2, 3], "y": [2, 4, 5], "type": "bar", "name": "Montréal"},
        ],
        layout={"title": "Dash Data Visualization"},
    )

    return fig
