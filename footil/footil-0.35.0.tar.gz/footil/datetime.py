"""Helpers for datetime manipulation."""
import datetime
from typing import Optional

DATETIME_FMT = '%Y-%m-%d %H:%M:%S'


def to_datetime(
    dt: str,
        fmt: Optional[str] = DATETIME_FMT) -> datetime.datetime:
    """Convert date/-time string to datetime.datetime object."""
    return datetime.datetime.strptime(dt, fmt)
