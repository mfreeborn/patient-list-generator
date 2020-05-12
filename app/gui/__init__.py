from pathlib import Path

LOGS_DIR = Path.cwd() / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# this goes at the end to avoid circular imports
from app.gui.gui import run_gui  # isort:skip  # noqa
