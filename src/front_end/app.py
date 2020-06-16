import dash
import dash_bootstrap_components as dbc
from flask_sqlalchemy import SQLAlchemy

from .. import settings, utils

app = dash.Dash(
    __name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.FLATLY],
)

utils.init_logging(app)

server = app.server
server.config["SQLALCHEMY_DATABASE_URI"] = settings.DB_URL
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(server)
