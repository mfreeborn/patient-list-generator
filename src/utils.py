import functools
import logging
import sys

from .front_end.layouts.enums import Element as El


logger = logging.getLogger()


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


def parse_trigger(ctx):
    """Return the triggering Element for a callback."""
    trigger = ctx.triggered[0]["prop_id"].split(".")[0]
    if not trigger:
        return None
    return El(trigger)
