from datetime import datetime

import pytz


def utcnow():
    """Get a timezone-aware datetime.now in UTC."""
    naive_utc = datetime.utcnow()
    return naive_utc.replace(tzinfo=pytz.UTC)


def timestamp_to_utc(timestamp: int):
    """Parse a timestamp into a UTC datetime object."""
    naive_utc = datetime.utcfromtimestamp(timestamp)
    return naive_utc.replace(tzinfo=pytz.UTC)
