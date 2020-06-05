import os

from dotenv import load_dotenv

load_dotenv()

try:
    DB_URL = os.environ["DB_URL"]
except KeyError:
    raise Exception("DB_URL environment variable missing!")
