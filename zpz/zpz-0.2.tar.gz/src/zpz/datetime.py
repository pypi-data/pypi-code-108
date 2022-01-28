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


def make_timestamp() -> str:
    '''
    This function creates a timestamp string with fixed format like

        '2020-08-22T08:09:13.401346'

    Strings created by this function can be compared to
    determine time order. There is no need to parse the string
    into `datetime` objects.

    The returned string is often written as a timestamp file, like

        open(file_name, 'w').write(make_timestamp())
    '''
    return datetime.utcnow().isoformat(timespec='microseconds')
