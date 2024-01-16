import os

from dotenv import load_dotenv

load_dotenv()
tz = os.environ.get("TZ", "US/Central")
