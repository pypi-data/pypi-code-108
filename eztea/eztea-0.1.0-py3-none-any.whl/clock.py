"""
A datetime helper with UTC timezone by default.
"""
from datetime import (  # noqa: F401
    MAXYEAR,
    MINYEAR,
    date,
    datetime,
    time,
    timedelta,
    timezone,
    tzinfo,
)
from typing import Union

import ciso8601

__all__ = (
    "date",
    "datetime",
    "time",
    "timedelta",
    "timezone",
    "tzinfo",
    "MINYEAR",
    "MAXYEAR",
    "UTC",
    "now",
    "is_timezone_aware",
    "format_iso8601",
    "parse_iso8601",
    "from_timestamp",
)


UTC = timezone.utc


def now() -> datetime:
    """Return now in UTC timezone"""
    return datetime.utcnow().replace(tzinfo=UTC)


def is_timezone_aware(value: Union[datetime, time]) -> bool:
    """
    Determine if a given datetime.datetime is timezone aware.

    The concept is defined in Python's docs:
    https://docs.python.org/library/datetime.html#datetime.tzinfo

    Assuming value.tzinfo is either None or a proper datetime.tzinfo,
    value.utcoffset() implements the appropriate logic.
    """
    return value.utcoffset() is not None


def format_iso8601(o: datetime) -> str:
    """
    Format datetime to ISO 8601 as well as ECMA-262 format.

    see also: eztea.json.JSONEncoder
    """
    r = o.isoformat()
    if o.microsecond:
        r = r[:23] + r[26:]
    if r.endswith("+00:00"):
        r = r[:-6] + "Z"
    return r


def parse_iso8601(string: str) -> datetime:
    """
    Parse datetime string and return timezone aware datetime object.
    Timezone default to UTC if not provided in datetime string.
    """
    value = ciso8601.parse_datetime(string)
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value


def from_timestamp(t: Union[int, float]) -> datetime:
    """
    Return datetime of the timestamp in UTC timezone.
    """
    return datetime.utcfromtimestamp(t).replace(tzinfo=UTC)
