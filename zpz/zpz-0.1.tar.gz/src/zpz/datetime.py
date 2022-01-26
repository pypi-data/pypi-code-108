__all__ = ['pacificnow']

from datetime import datetime

from pytz import timezone


def tznow(tzname):
    """
    Get the current ``datetime`` in the specified timezone.

    Args:
        tzname: the ISO standard timezone name,
        such as ``Africa/Cairo``, ``America/Los_Angeles``.
    """
    return datetime.now(timezone(tzname))


def pacificnow():
    return tznow('America/Los_Angeles')
