import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

TESTING = os.environ.get("TESTING", "false").lower() == "true"
if TESTING:
    DB_URL = "sqlite://"
else:
    try:
        DB_URL = os.environ["DB_URL"]
    except KeyError:
        raise Exception("DB_URL environment variable is required")

try:
    LIST_ROOT_DIR = Path(os.environ["LIST_ROOT_DIR"])
except KeyError:
    raise Exception("LIST_ROOT_DIR environment variable is required")

DEBUG = os.environ.get("DEBUG", "true").lower() == "true"

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", 8080))
