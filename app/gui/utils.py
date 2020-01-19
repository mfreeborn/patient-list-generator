import datetime
import os
import subprocess
from pprint import pprint
from app.gui.enums import Key


def log_gui_event(event: str, values: dict):
    """Helper function for logging events in the gui.

    Specifically conceals sensitive information before printing."""
    # make a copy of the values dict so we don't overwrite anything permanently
    values = dict(values)
    values[Key.CAREFLOW_PASSWORD_INPUT] = "*" * 5 if values[Key.CAREFLOW_PASSWORD_INPUT] else ""
    values[Key.TRAKCARE_PASSWORD_INPUT] = "*" * 5 if values[Key.TRAKCARE_PASSWORD_INPUT] else ""

    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
    print()
    print(event)
    pprint(values)
    print()
    print("-" * 30)
    print()

def open_folder(path: str):
    if os.name == "nt":
        # Windows
        os.startfile(path)
    else:
        # Linux
        subprocess.Popen(["xdg-open", path])
