"""time tools tools Copyright 2020 Caliber Data Labs."""
#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#

import math
import sys
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Union

import dateutil.parser
import pytz
from dateutil.relativedelta import relativedelta

from ..constants import Time

START_OF_TIME_STRING = Time.START_OF_TIME_STRING
START_OF_TIME_DATETIME = Time.START_OF_TIME_DATETIME
END_OF_TIME_STRING = Time.END_OF_TIME_STRING
END_OF_TIME_DATETIME = Time.END_OF_TIME_DATETIME

epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)


def day_string_from_isoformat_string(ios_timestamp):
    return ios_timestamp.split("T")[0]


def day_string_from_timestamp(timestamp):
    """getting the YYYY-MM-DD time format from a timestamp.

    :param timestamp: input timestamp
    :return: day string in YYYY-MM-DD
    """
    return "{:04d}-{:02d}-{:02d}".format(timestamp.year,
                                         timestamp.month, timestamp.day)


def convert_dict_timestamps_to_string(d, keys):
    for k in keys:
        val = d.get(k)
        if val and isinstance(val, datetime):
            d[k] = datetime_to_iso_utc(val)
    return d


def get_millisecond_from_epoch(timestamp):
    return int((timestamp - epoch).total_seconds() * 1000)


def get_seconds_from_epoch(timestamp):
    return (timestamp - epoch).total_seconds()


def days_between(start_date, end_date):
    end = start_date
    while end < end_date:
        start = end
        end = start + timedelta(1)
        yield start, end


def string_to_datetime(date_string):
    try:
        return dateutil.parser.parse(date_string).astimezone(tz=pytz.utc)
    except ValueError:
        return dateutil.parser.parse(date_string).replace(tzinfo=pytz.utc)


def epoch_to_iso_utc(epoch_time):
    return datetime.utcfromtimestamp(
        epoch_time).replace(tzinfo=pytz.utc).isoformat()


def epoch_to_iso(epoch_time):
    return datetime.utcfromtimestamp(epoch_time).replace(tzinfo=pytz.utc)


def datetime_to_iso_utc(timestamp: datetime) -> str:
    try:
        return timestamp.astimezone(tz=pytz.utc).isoformat()
    except ValueError:
        return timestamp.replace(tzinfo=pytz.utc).isoformat()


def datetime_or_str_to_iso_utc(timestamp: Union[datetime, str]) -> str:
    if isinstance(timestamp, str):
        return timestamp
    else:
        return datetime_to_iso_utc(timestamp)


def str_or_datetime_to_datetime(timestamp: Union[datetime, str]) -> datetime:
    if isinstance(timestamp, datetime):
        return timestamp
    else:
        return string_to_datetime(timestamp)


def datetime_from_seconds(seconds):
    return datetime.fromtimestamp(seconds)


def revert_to_datetime_utc(timestamp):
    """revert string or timestamp to tz_aware timestamp in UTC.

    :param timestamp:
    :return:
    """

    # if datetime
    if isinstance(timestamp, datetime):
        try:
            return timestamp.astimezone(tz=pytz.utc)
        except ValueError:
            return timestamp.replace(tzinfo=pytz.utc)
    # if string
    else:
        return string_to_datetime(timestamp)


def get_relative_time_delta(interval_size, num_intervals, negative=True):
    if negative:
        sign = -1
    else:
        sign = 1

    interval_delta = sign * num_intervals
    time_map = {
        "1h": relativedelta(hours=interval_delta),
        "1d": relativedelta(days=interval_delta),
        "1w": relativedelta(weeks=interval_delta),
        "1M": relativedelta(months=interval_delta),
        "1y": relativedelta(years=interval_delta),
    }
    if interval_size in time_map:
        return time_map[interval_size]
    else:
        raise ValueError("Invalid interval size : {}".format(interval_size))


def get_datetime_utc_from_ros_time(ros_time) -> datetime:
    return datetime.utcfromtimestamp(
        ros_time.secs + ros_time.nsecs * 1e-9).replace(tzinfo=pytz.utc)


def get_time_delta_from_interval(interval: str) -> relativedelta:
    """Get the time delta for the interval."""
    if interval == "second":
        return relativedelta(seconds=1)
    elif interval == "minute":
        return relativedelta(minutes=1)
    elif interval == "hour":
        return relativedelta(hours=1)
    else:
        raise ValueError("Supported intervals are second,minute,hour")


def get_datetime_from_year_and_doy(
        year_doy: str,
        time_zone: str = None) -> datetime:
    if not time_zone:
        return (datetime(int(year_doy[:4]), 1, 1, 12, 0, 0)
                + timedelta(int(year_doy[-3:]) - 1)).astimezone(tz=pytz.utc)
    return (datetime(int(year_doy[:4]), 1, 1, 12, 0, 0)
            + timedelta(int(year_doy[-3:]) - 1)).astimezone(tz=pytz.timezone(time_zone))


def add_minutes(t: datetime, delta_t: int = 60) -> datetime:
    return t + timedelta(minutes=delta_t)


def convert_timestamp_to_time_index(
        resolution: float,
        seconds_since_epoch: float) -> int:
    return int(
        math.floor(
            (seconds_since_epoch
             - Time.START_OF_TIME_DATETIME.timestamp()) /
            resolution))


def merge_time_intervals(
        times: List[Tuple[datetime, datetime]]) -> Tuple[Tuple[datetime, datetime], bool]:
    has_overlap = True
    merged_time = times[0]
    st, et = times[1]
    if st > merged_time[1] or et < merged_time[0]:
        has_overlap = False
        return merged_time, has_overlap
    elif st > merged_time[0] and et < merged_time[1]:
        return merged_time, has_overlap
    elif merged_time[0] < et < merged_time[1]:
        return (st, merged_time[1]), has_overlap
    elif merged_time[0] < st < merged_time[1]:
        return (merged_time[0], et), has_overlap


def time_index_to_timestamp(time_index: int, resolution: float) -> datetime:
    return Time.START_OF_TIME_DATETIME + \
        timedelta(seconds=time_index * resolution)


def get_elapsed_time(end_time: datetime, start_time: datetime):
    return (end_time - start_time).total_seconds()


def jsonify_metadata(metadata: dict,
                     timestamp_keys: Optional[list] = None) -> dict:
    if timestamp_keys is None:
        timestamp_keys = ["timestamp", "start_time", "end_time"]
    # Format the timestamp as str
    for timestamp_key in timestamp_keys:
        timestamp = metadata.get(timestamp_key)
        if timestamp:
            if isinstance(timestamp, datetime):
                metadata[timestamp_key] = timestamp.astimezone(
                    tz=pytz.utc).isoformat()
    return metadata
