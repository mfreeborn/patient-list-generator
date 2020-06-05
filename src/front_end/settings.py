import os

from dotenv import load_dotenv

load_dotenv()

try:
    DB_URL = os.environ["DB_URL"]
except KeyError:
    raise Exception("DB_URL environment variable missing!")

DEBUG = os.environ.get("DEBUG", "true").lower() == "true"

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", 8080))
