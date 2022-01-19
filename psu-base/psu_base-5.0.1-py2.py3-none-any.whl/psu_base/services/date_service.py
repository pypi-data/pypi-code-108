import re
import math
from datetime import datetime
import arrow


def string_to_date(date_string):
    """
    Convert any reasonable date string into a date
    """

    # NEW LOGIC FOR DATES CONTAINING MONTH NAMES  <----------------------------
    date_string = date_string.replace("a.m.", "am").replace("p.m.", "pm").upper()
    months = {
        "JANUARY": 1,
        "FEBRUARY": 2,
        "MARCH": 3,
        "APRIL": 4,
        "MAY": 5,
        "JUNE": 6,
        "JULY": 7,
        "AUGUST": 8,
        "SEPTEMBER": 9,
        "OCTOBER": 10,
        "NOVEMBER": 11,
        "DECEMBER": 12,
    }
    had_month_name = False
    for mmm, mm in months.items():
        if mmm in date_string:
            had_month_name = True
            if f"{mmm} " in date_string:
                date_string = date_string.replace(f"{mmm} ", f"{mm}/")
            else:
                date_string = date_string.replace(mmm, f"{mm}/")
    if had_month_name:
        time_str = re.search(r"(\d{1,2}:\d{1,2})", date_string, re.IGNORECASE)
        if time_str:
            date_str = (
                date_string[: date_string.index(time_str.group(1))]
                .replace(" ", "")
                .strip()
                .strip(",")
            )
            time_str = date_string[date_string.index(time_str.group(1)) :].strip()
            date_string = f"{date_str} {time_str}"
    # END LOGIC FOR DATES CONTAINING MONTH NAMES  <----------------------------

    # Replace any date separators with forward slashes
    date_string = re.sub(r"[-.,;\\]", "/", date_string)

    # HTML "datetime-local" inputs use format: 2020-08-13T10:15
    # Just replacing the T with a space will allow this to be recognized
    if re.sub(r"[^a-zA-Z]", r"", date_string) == "T":
        date_string = date_string.replace("T", " ")

    # Determine the date format
    date_format = None
    if re.match(r"\d{8,}", date_string, re.IGNORECASE):
        date_format = "%Y%m%d"

    elif re.match(r"\d{4}/\d{1,2}/\d{1,2}", date_string, re.IGNORECASE):
        date_format = "%Y/%m/%d"

    elif re.match(r"\d{1,2}/\D{3}/\d{4}", date_string, re.IGNORECASE):
        date_format = "%d/%b/%Y"
    elif re.match(r"\d{1,2}/\D{3}/\d{2}", date_string, re.IGNORECASE):
        date_format = "%d/%b/%y"

    elif re.match(r"\d{1,2}/\d{1,2}/\d{4}", date_string, re.IGNORECASE):
        date_format = "%m/%d/%Y"
    elif re.match(r"\d{1,2}/\d{1,2}/\d{2}", date_string, re.IGNORECASE):
        date_format = "%m/%d/%y"

    # If only a time (no date) is given, assume today
    today = date_format is None and ":" in date_string

    # If adding time to today's date, need to start with an empty string
    if today:
        date_format = ""

    # Look for time format
    if re.match(r"\d{14}", date_string, re.IGNORECASE):
        date_format += "%H%M%S"
    elif re.match(r"\d{12}", date_string, re.IGNORECASE):
        date_format += "%H%M"
    elif re.match(r"\d{10}", date_string, re.IGNORECASE):
        date_format += "%H"

    elif re.match(
        r"\S+\s+\d{1,2}:\d{1,2}:\d{1,2}\s+[apm]{2}", date_string, re.IGNORECASE
    ):
        date_format += " %I:%M:%S %p"
    elif re.match(r"\S+\s+\d{1,2}:\d{1,2}:\d{1,2}/\d{6}", date_string, re.IGNORECASE):
        date_format += " %H:%M:%S/%f"
    elif re.match(r"\S+\s+\d{1,2}:\d{1,2}:\d{1,2}", date_string, re.IGNORECASE):
        date_format += " %H:%M:%S"

    elif re.match(r"\S+\s+\d{1,2}:\d{1,2}\s+[apm]{2}", date_string, re.IGNORECASE):
        date_format += " %I:%M %p"
    elif re.match(r"\S+\s+\d{1,2}:\d{1,2}", date_string, re.IGNORECASE):
        date_format += " %H:%M"

    # If adding time to today, add today to the string
    if today and len(date_format) > 0:
        date_string = "{0} {1}".format(datetime.now().strftime("%Y/%m/%d"), date_string)
        date_format = "%Y/%m/%d {0}".format(date_format)

    if date_format and date_format != "":
        return datetime.strptime(date_string, date_format)
    else:
        return None


def seconds_to_duration_description(num_seconds):
    """Given a number of seconds, return a text description of how long it is"""
    # Pull out days
    num_days = math.floor(num_seconds / 60 / 60 / 24)
    num_seconds -= num_days * 60 * 60 * 24
    # Pull out hours
    num_hours = math.floor(num_seconds / 60 / 60)
    num_seconds = num_seconds - (num_hours * 60 * 60)
    # Pull out minutes
    num_mins = math.floor(num_seconds / 60)
    num_seconds = num_seconds - (num_mins * 60)

    # Build a descriptive string
    description = []
    if num_days:
        description.append(f"{num_days} day{'s' if num_days != 1 else ''},")
    if num_hours:
        description.append(f"{num_hours} hour{'s' if num_hours != 1 else ''},")
    if num_mins:
        description.append(f"{num_mins} minute{'s' if num_mins != 1 else ''}")
    if num_seconds or not description:
        if description:
            description.append("and")
        description.append(f"{num_seconds} second{'s' if num_seconds != 1 else ''}")
    return " ".join(description).strip(" ,")
