import calendar
from datetime import date, datetime, timedelta
from typing import Union

import dateparser
from django.utils import timezone

from jnt_django_toolbox.consts.time import (
    SECONDS_PER_DAY,
    SECONDS_PER_HOUR,
    SECONDS_PER_MINUTE,
)

Number = Union[int, float]


def date2datetime(value: date) -> datetime:  # noqa: WPS110
    """Converts date to datetime."""
    return datetime.combine(value, datetime.min.time())


def begin_of_week(target: date, first_weekday: int = calendar.MONDAY) -> date:
    """Get begin of week."""
    days_passed = target.weekday() - first_weekday

    if days_passed < 0:
        days_passed += 7

    return target - timedelta(days=days_passed)


def humanize_time(total_seconds: Number) -> str:
    """Provides human friendly representation for seconds."""
    if not isinstance(total_seconds, (int, float)):
        raise ValueError("Seconds should be a number")

    if total_seconds == 0:
        return "0s"

    items = []

    time_units = (
        ("d", SECONDS_PER_DAY),
        ("h", SECONDS_PER_HOUR),
        ("m", SECONDS_PER_MINUTE),
        ("s", 1),
    )

    for unit, sec_in_unit in time_units:
        val = total_seconds // sec_in_unit
        if not val:
            continue

        items.append("{0}{1}".format(int(val), unit))
        total_seconds -= sec_in_unit * val
        if not total_seconds:
            break

    return " ".join(items)


epoch = datetime.utcfromtimestamp(0)


def unix_time_seconds(dt):
    """Get unix time from datetime."""
    return (dt.replace(tzinfo=None) - epoch).total_seconds()


def parse_human_date(date_str: str):
    """Parse human presented date string."""
    return timezone.make_aware(dateparser.parse(date_str))
