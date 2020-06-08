import functools
import logging
import sys

from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator

from . import settings
from .front_end.layouts.enums import Element as El

logger = logging.getLogger()


class NHSNumber(TypeDecorator):
    """Store NHS numbers without spaces; return them with spaces."""

    impl = Text

    def process_bind_param(self, value, dialect):
        if value:
            return "".join(value.split())
        return ""

    def process_result_value(self, value, dialect):
        if value:
            value = "".join(value.split())
            return f"{value[:3]} {value[3:6]} {value[6:]}"
        return ""


def build_team_file_path(team, date):
    """Return a path to a folder constructed from a team name and a date."""
    return settings.LIST_ROOT_DIR / f"{team.name}" / f"{date:%Y}" / f"{date:%m - %B}"


def generate_file_stem(team, date):
    """Create a file stem (i.e. no file extension) derived from the team name and the date."""
    return f"{date:%d-%m-%Y}_{team.name}".lower()


def init_logging(app):
    # set up a standard logger to stdout
    logging.basicConfig(
        format="%(asctime)s:%(levelname)s:%(name)s:%(filename)s:%(lineno)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        level=logging.DEBUG,
    )

    # get rid of the default Dash logging handler - it only duplicates
    # some logs but without nice formatting
    app.logger.handlers.pop()

    # raise the log level of the werkzeug level so we don't get spammed by it
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.setLevel(logging.WARN)


def log_callback(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        logger.debug(
            "The callback '%s' was called with these args: %s",
            fn.__name__,
            # truncate very long args e.g. base64-encoded files
            ", ".join(str(arg)[:30] for arg in args),
        )
        return fn(*args, **kwargs)

    return wrapper


def parse_trigger(ctx):
    """Return the triggering Element for a callback."""
    trigger = ctx.triggered[0]["prop_id"].split(".")[0]
    if not trigger:
        return None
    return El(trigger)


def pluralise(word, count):
    """Crudely pluralise the given word based on the given count."""
    if count == 1:
        return word
    return word + "s"
