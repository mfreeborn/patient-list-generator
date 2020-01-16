from pprint import pprint
import datetime


def log_gui(event: str, values: dict):
    """Helper function for logging events in the gui.

    Specifically conceals sensitive information before printing."""
    # make a copy of the values dict so we don't overwrite anything permanently
    values = dict(values)
    values["careflow_password"] = "*" * 5 if values["careflow_password"] else ""
    values["trakcare_password"] = "*" * 5 if values["trakcare_password"] else ""

    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
    print()
    print(event)
    pprint(values)
    print()
    print("-" * 30)
    print()
