from pathlib import Path

from app.gui.enums import Key

LOGS_DIR = Path.cwd() / "logs"
LOGS_DIR.mkdir(exist_ok=True)

credential_keys = (
    Key.CAREFLOW_USERNAME_INPUT,
    Key.CAREFLOW_PASSWORD_INPUT,
    Key.TRAKCARE_USERNAME_INPUT,
    Key.TRAKCARE_PASSWORD_INPUT,
)

# this goes at the end to acoid circular imports
from app.gui.gui import run_gui  # isort:skip  # noqa
