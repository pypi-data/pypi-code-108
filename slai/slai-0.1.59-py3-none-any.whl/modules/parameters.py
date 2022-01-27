import os
from dotenv import load_dotenv

load_dotenv(override=True)


def from_config(key, default):
    value = os.getenv(key, default)
    return value
