import logging

from app.gui import run_gui
from app.utils import init_logging

if __name__ == "__main__":
    init_logging(level=logging.DEBUG)
    run_gui()
