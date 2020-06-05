from .app import app
from .layouts import BASE_LAYOUT
from . import callbacks

app.layout = BASE_LAYOUT


def run_server():
    app.run_server(debug=settings.DEBUG, host=settings.HOST, port=settings.PORT)
