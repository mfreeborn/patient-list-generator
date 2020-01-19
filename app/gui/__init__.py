from app.gui.enums import Key

credential_keys = (
    Key.CAREFLOW_USERNAME_INPUT,
    Key.CAREFLOW_PASSWORD_INPUT,
    Key.TRAKCARE_USERNAME_INPUT,
    Key.TRAKCARE_PASSWORD_INPUT,
)


# this goes at the end to acoid circular imports with `credential_keys`
from app.gui.gui import run_gui  # noqa
