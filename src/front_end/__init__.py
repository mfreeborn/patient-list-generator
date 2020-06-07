from .. import settings
from . import callbacks  # noqa
from .app import app
from .layouts import BASE_LAYOUT

app.layout = BASE_LAYOUT


def run_server():
    app.logger.info(
        "Starting server at host %s running on port %d; DEBUG mode is %s",
        settings.HOST,
        settings.PORT,
        "on" if settings.DEBUG else "off",
    )
    app.run_server(debug=settings.DEBUG, host=settings.HOST, port=settings.PORT)
