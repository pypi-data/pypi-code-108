import os
import yaml
from daybook.domain.model import Reader
from datetime import date, datetime, timedelta


MAIN_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "main_settings.yml")


def get_current_reading_period_start() -> date:
    reading_period_start = None
    now = datetime.now()
    with open(MAIN_SETTINGS_FILE, "r") as file:
        settings = yaml.safe_load(file)
    period_len_in_days = settings["reading_period_length_in_days"]
    reading_period_start = now - timedelta(days=period_len_in_days)
    return reading_period_start.date()


def get_valid_reader(reader_name: str) -> Reader:
    if reader_name is None:
        with open(MAIN_SETTINGS_FILE, "r") as file:
            settings = yaml.safe_load(file)
            reader_name = settings["last_reading_log_used"]
            while not reader_name:
                reader_name = input("Reader's name? ")
    else:
        save_default_reader_to_settings(reader_name)
    return Reader(reader_name)


def get_default_reading_log_reader() -> Reader:
    reader = None
    with open(MAIN_SETTINGS_FILE, "r") as file:
        settings = yaml.safe_load(file)
        reader_name = settings["last_reading_log_used"]
        reader = Reader(reader_name)
    return reader


def save_settings(settings):
    with open(MAIN_SETTINGS_FILE, "w") as file:
        yaml.dump(settings, file)


def save_default_reader_to_settings(default_reader: Reader):
    with open(MAIN_SETTINGS_FILE, "r") as file:
        settings = yaml.safe_load(file)
    settings["last_reading_log_used"] = default_reader if default_reader else "~"
    save_settings(settings)


def set_default_reading_log_reader(reader: Reader):
    with open(MAIN_SETTINGS_FILE, "r") as file:
        settings = yaml.safe_load(file)
    settings["last_reading_log_used"] = reader if reader else "~"
    save_settings(settings)
