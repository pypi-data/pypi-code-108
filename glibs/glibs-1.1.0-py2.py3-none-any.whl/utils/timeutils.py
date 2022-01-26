import ciso8601
import datetime
from dateutil import parser, tz


def to_isoformat(date):  # type: (datetime.datetime) -> str
    """Returns a datetime formatted as ISO-8601 with Z flag automatically"""
    # since datetime is naive we add the UTC flag manually
    return date.isoformat() + "Z"


def from_isoformat(date_str):  # type: (str) -> datetime.datetime
    """Parse a ISO-8601 string and returns a datetime.datetime"""

    # Optimize most common scenario
    # https://github.com/elasticsales/ciso8601
    if date_str[-1] == "Z":
        return ciso8601.parse_datetime_unaware(date_str)
    date = parser.parse(date_str)
    if date.tzinfo:
        date = date.astimezone(tz.tzutc()).replace(tzinfo=None)
    return date
