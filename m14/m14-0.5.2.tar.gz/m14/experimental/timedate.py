#!/usr/bin/env python3
# coding: utf-8

import datetime
import re
from datetime import timedelta
from typing import Union


def parse_time(time_string: str):
    """
    >>> parse_time('00:03:02,521')
    datetime.timedelta(seconds=182, microseconds=521000)
    """
    regex = re.compile('^([0-9]+):([0-9]+):([0-9]+),([0-9]+)$')
    match = regex.match(time_string)
    if match is None:
        raise ValueError("Unparseable timestamp: {}".format(time_string))
    hrs, mins, secs, msecs = map(int, match.groups())
    return timedelta(hours=hrs, minutes=mins, seconds=secs, milliseconds=msecs)


def datetime_from_timestamp_epoch1601(ts_1601: float, unit: int = 0):
    """
    Args:
        ts_1601: time since 1 January 1601
        unit: 0 = second, 6 = microsecond, 7 = 100 nanosecond
    Returns:
        a datetime.datetime instance
    See Also:
        https://en.wikipedia.org/wiki/Epoch_(computing)#Notable_epoch_dates_in_computing
    """
    # https://stackoverflow.com/a/26118615/2925169
    unit_per_sec = 10 ** unit
    ts = ts_1601 / unit_per_sec - 11644473600
    return datetime.datetime.fromtimestamp(ts)


datetime_from_timestamp_1601 = datetime_from_timestamp_epoch1601


def fmt_today(fmt='-') -> Union[str, datetime.date]:
    return relative_date(0, fmt)


def relative_date(delta: int = 0, fmt='-') -> Union[str, datetime.date]:
    date = datetime.date.today()
    if delta:
        date += datetime.timedelta(days=delta)
    if fmt is None:
        return date
    elif fmt == '':
        return date.strftime('%Y%m%d')
    elif fmt == '-':
        return date.strftime('%Y-%m-%d')
    return date.strftime(fmt)
