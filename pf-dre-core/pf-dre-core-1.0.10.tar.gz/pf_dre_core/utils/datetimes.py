# Built-in Modules
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Any, Union, Optional, TypedDict, Type

# Third party modules
import numpy as np

logger = logging.getLogger(__name__)

NEM_TRADING_MINS = int(os.environ['NEM_TRADING_PERIOD'])


class SignedTimedelta(TypedDict):
    sign: int
    delta: timedelta


def offset_string_to_timedelta(offset_string: str) \
        -> Type[Union[SignedTimedelta, None]]:
    """
    Given a string of a specific format, specifically:
        "[.. hr] [.. m]"
    Return a timedelta object and sign.
    :param offset_string: The string to be checked for the any offset time
    patterns.
    :return: A dictionary containing the 'sign' (1, -1) and 'delta' (timedelta)
    of the offset if a valid offset string is found, otherwise None.
    """
    regex = re.compile(re.compile(r'((?P<hours>\d+?)hr)?((?P<minutes>\d+?)m)?'))
    parts = regex.match(offset_string)
    parts_dict = {k: v for k, v in parts.groupdict().items() if v is not None}
    if bool(parts_dict):
        logger.debug("Timestamp ")
        time_delta_params = {}
        for name, val in parts_dict.items():
            if val:
                time_delta_params[name] = int(val)
        logger.debug("Timestamp has the following time offset params "
                     "{}".format(time_delta_params))
        return {
            'sign': 1,
            'delta': timedelta(**time_delta_params)
        }
    else:
        logger.debug("No offset identified in ref_t modifier string")
        return None


def validate_ts(ref_t: datetime,
                ts_string: Optional[str] = None,
                end: Optional[bool] = False) -> datetime:
    """
    :param ref_t: Reference timestamp, not directly used in this function.
    :param ts_string: Timestamp string. Will either be in ISO Format, or be
    represent one of the modification strings (which will be processed when
    passed to modify_ts function.
    :param end: Flags whether the reference timestamp is at the start or end of
    a time range.
    :return: Validated timestamp, after any modifications have been performed
    (if necessary).
    """
    if ts_string is None:
        if end:
            return ref_t
        else:
            logger.error("Starting timestamp was not of type 'str'")
            raise ValueError
    else:
        try:
            return datetime.fromisoformat(ts_string)
        except ValueError:
            return modify_ts(ref_t, modifier=ts_string, end=end)


def modify_ts(ref_t: datetime,
              modifier: Optional[str] = None,
              end: Optional[bool] = False) -> datetime:
    """
    By passing a reference datetime, use a modifier string to generate a
    modified datetime. The modification may be dependent on whether the
    timestamp relates to the start or end of a time range.
    :param ref_t: Raw reference timestamp.
    :param modifier: String which results in the transformation of the resulting
    datetime. The modifier string defines date/time changes relative to ref_t.
    :param end: Flags whether the reference timestamp is at the start or end of
    a time range.
    :return: Modified timestamp, after any modifications have been performed.
    """

    if isinstance(modifier, str):
        offset = offset_string_to_timedelta(modifier)
        if isinstance(offset, dict):
            return ref_t + offset['sign']*offset['delta']
        if modifier.lower() == 'trading period':
            if end:
                return round_datetime(ref_t, 'up', 5)
            else:
                return round_datetime(ref_t, 'down', NEM_TRADING_MINS)
        if modifier.lower() == 'this month':
            if end:
                return ref_t
            else:

                return ref_t.replace(day=1, hour=0, minute=0,
                                     second=0, microsecond=0)


def round_np_dt64(np_dt: np.datetime64, direction: str,
                  minutes: int) -> np.datetime64:
    """
    Rounds up a numpy datetime64 object to the nearest 'X' minutes and returns
    as a numpy datetime64 object.
    :param np_dt: The numpy datetime64 object
    :param direction: 'up' or 'down' (anything but 'up')
    :param minutes: The number of minutes to round to (relative to the
    current hour.
    :return: The rounded up numpy datetime64 object.
    """
    dt = np_dt64_to_datetime(np_dt)
    rounded_dt = round_datetime(dt, direction, minutes)
    return np.datetime64(rounded_dt)


def round_datetime(dt: datetime, direction: str, minutes: int) -> datetime:
    """
    Round a python datetime up or dawn to the desired resolution in minutes
    :param dt: datetime object to round
    :param direction: 'up' or 'down' (anything but 'up')
    :param minutes: Desired Resolution in Minutes
    :return: A rounded datetime to minute precision
    """
    new_minute = (dt.minute // minutes +
                  (1 if direction == 'up' else 0)) * minutes
    return dt + timedelta(minutes=new_minute - dt.minute,
                          seconds=-dt.second,
                          microseconds=-dt.microsecond)


def np_dt64_to_datetime(date):
    """
    Converts a numpy datetime64 object to a python datetime object
    Input:
      date - a np.datetime64 object
    Output:
      DATE - a python datetime object
    """
    timestamp = ((date - np.datetime64('1970-01-01T00:00:00'))
                 / np.timedelta64(1, 's'))
    return datetime.utcfromtimestamp(timestamp)


def create_timestamp_array(start_date, end_date, delta):
    """
    Creates a timestamped array from start_date to end_date in increments of
    delta which is a datetime timedelta object
    """
    result = []
    nxt = start_date
    while nxt <= end_date:
        result.append(nxt)
        nxt += delta
    return result