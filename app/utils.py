import logging
import sys


def init_logging(level=None):
    """Helper function for configuring logging."""
    if level is None:
        level = logging.INFO

    logger = logging.getLogger("PLG")
    logger.setLevel(level)
    logger.propagate = False

    stdout_streamhandler = logging.StreamHandler(stream=sys.stdout)

    formatter = logging.Formatter(
        fmt="%(asctime)s:%(levelname)s:%(name)s:%(filename)s:%(lineno)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stdout_streamhandler.setFormatter(formatter)

    logger.addHandler(stdout_streamhandler)

    logger.debug("Logging initialisation complete")
