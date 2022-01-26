"""
Function to convert arbitrary datetime strings to ISO 1806 format.
"""

from datetime import datetime


def to_datetime(d: str) -> datetime:
    """
    Convert an arbitrary date string to ISO format.

    :param d: A date string.
    :type d: str
    :raises ValueError: If the date string can't be parsed.
    :return: The date string in ISO format.
    :rtype: datetime
    """
    if not isinstance(d, str):
        raise TypeError(f"Expected a string, got {type(d)}")

    time_fns = [
        datetime.fromisoformat,
        lambda date_string: datetime.strptime(
            date_string, "%Y-%m-%d %H:%M:%S.%f %z %Z"
        ),
        lambda date_string: datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ"),
        lambda date_string: datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f%z"),
    ]

    for time_fn in time_fns:
        try:
            return time_fn(d)
        except ValueError:
            continue
    raise ValueError(f"Could not parse date string: {d}")
