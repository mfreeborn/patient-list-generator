import logging


def init_logging(level=None):
    """Helper function for configuring logging."""
    if level is None:
        level = logging.INFO
    logging.basicConfig(
        format="%(levelname)s:%(name)s:%(module)s:%(lineno)s: %(message)s",
        datefmt="%y-%m-%d %H:%M:%S",
        level=level,
    )
