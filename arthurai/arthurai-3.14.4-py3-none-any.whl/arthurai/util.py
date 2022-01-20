from datetime import datetime, timedelta
from dateutil.parser import isoparse
import pytz
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Union, Type

from arthurai.common.constants import ValueType
from arthurai.common.exceptions import UserTypeError, UserValueError, InternalValueError


logger = logging.getLogger(__name__)


"""
Only client facing functions should live in this module. If a util  is used for a specific package and not client facing
it should be added to that packages util.py file.
"""


def format_timestamps(inferences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Checks list of json inferences to ensure their timestamps have been converted to ISO8601 conventions.

    :param inferences: Input to `send_inferences()` function.

    :return: updated list of json inferences with ISO8601 formatted timestamps
    :raise: TypeError: timestamp is not of type `datetime.datetime`
    :raise: ValueError: timestamp is not timezone aware and no location data is provided to remedy
    """
    # TODO: deprecate support for strings and delete conditional
    #  @ https://arthurai.atlassian.net/jira/software/projects/CR/boards/11?selectedIssue=CR-10
    if len(inferences) > 0 and (
        is_string_date(inferences[0].get("inference_timestamp"))
        or is_string_date(inferences[0].get("ground_truth_timestamp"))
    ):
        date_to_log = inferences[0].get("inference_timestamp") or inferences[0].get(
            "ground_truth_timestamp"
        )
        logger.warning(
            f"DEPRECATION WARNING: Your provided timestamps starting with: {date_to_log} is of type `str` and is "
            f"assumed to be in UTC format. Timezone information will be ignored. `str` types will be deprecated. "
            f"Please use timeaware `datetime.datetime` timestamps and use `arthurai.util.format_timestamp` if needed, "
            f"e.g. `format_timestamp(datetime.strptime('2020-01-01 01:01:01', '%Y-%m-%d %H:%M:%S'), 'US/Eastern')`."
        )

    for inf in inferences:
        for timestamp_key in ["inference_timestamp", "ground_truth_timestamp"]:
            if timestamp_key in inf:
                inf[timestamp_key] = format_timestamp(inf[timestamp_key])
    return inferences


def format_timestamp(timestamp: Union[datetime, str], location: Optional[str] = None) -> str:
    """Check if timestamp is time aware and convert to ISO8601 conventioned string.

    This helper function converts datetime objects into timezone aware ISO8601 strings, which is necessary when sending
    JSON to Arthur's backend. If `timestamp` argument is timezone aware, no `location` needs to be provided; otherwise,
    a string pytz `location` like "US/Eastern" needs to be provided to establish timezone. String `timestamp` are
    supported for backwards compatability and for simplicity are assumed to already be in UTC format, but string support
    will be deprecated.

    :param timestamp: timestamp to format
    :param location: pytz location as string

    :return: ISO8601 formatted timestamp
    :raise: TypeError: timestamp is not of type `datetime.datetime`
    :raise: ValueError: timestamp is not timezone aware and no location data is provided to remedy
    """

    # TODO: deprecate support for strings and delete conditional
    #  @ https://arthurai.atlassian.net/jira/software/projects/CR/boards/11?selectedIssue=CR-10
    if isinstance(timestamp, str):
        if timestamp[-1] != "Z":
            return timestamp + "Z"
        return timestamp

    if not (location is None or isinstance(location, str)):
        raise UserTypeError(f"`location` must be valid pytz string like 'US/Eastern' or None type")

    localization = pytz.timezone(location) if location else None

    if not isinstance(timestamp, datetime):
        raise UserTypeError(
            f"`timestamp` {timestamp} must be of type `datetime.datetime`, not {type(timestamp)}."
        )

    if not (
        timestamp.tzinfo is not None
        and timestamp.tzinfo.utcoffset(timestamp) is not None
    ):
        if localization:
            return (
                localization.localize(timestamp).astimezone(pytz.utc).isoformat()[:-6]
                + "Z"
            )  # convert to utc, log warning if converting from non-utc to utc
        else:
            raise UserValueError(
                f"`timestamp` {timestamp} is not timezone aware, please supply pytz `timezone` string to make "
                f"timestamp timezone aware, e.g. `format_timestamp(datetime.datetime(2021, 1, 1), 'US/Eastern')`."
            )
    return timestamp.astimezone(pytz.utc).isoformat()[:-6] + "Z"


# TODO: deprecate support for strings and delete method
#  @ https://arthurai.atlassian.net/jira/software/projects/CR/boards/11?selectedIssue=CR-10
def is_string_date(string: Any) -> bool:
    """
    Return whether the string can be interpreted as a (partial) ISO-8601 date.

    :param string: str, string to check for date
    """
    if not isinstance(string, str) or string.isdigit():
        return False
    try:
        isoparse(string)
    except ValueError:
        return False
    else:
        return True


def normal_random_ints_fixed_sum(num_values: int, total_sum: int, relative_std_dev: float = 0.5) -> np.ndarray:
    """
    Return `num_values` roughly normally-distributed integers summing to `total_sum`. Numbers are first sampled from
    the normal distribution, then adjusted to fit the sum. Adjustments are made first by shifting the resulting
    distribution to be at least `total_sum`, then decrementing a subset of the values to match `total_sum`.
    :param num_values: number of integers to return
    :param total_sum: total sum the integers returned
    :param relative_std_dev: the relative standard deviation (std_dev / mean) of the initial distribution.
    :return:
    """
    # first pull from the normal distribution to get some initial values
    mean_value = total_sum / num_values
    std_dev = mean_value * relative_std_dev
    initial_values = np.round(np.random.normal(loc=mean_value, scale=std_dev, size=num_values)).astype(np.int64)
    # bump any negatives values up to zero
    positive_values = np.clip(initial_values, a_min=0, a_max=None)

    # shift the distribution to get close to the correct sum
    mean_diff_floor = np.floor((positive_values.sum() - total_sum) / num_values).astype(np.int64)
    values = positive_values - mean_diff_floor

    # now our difference must be less than the length of the array, and positive
    final_difference = values.sum() - total_sum
    # we can simply subtract 1 from however many indices we need to to reach the exact sum
    inds_to_decrement = np.random.choice(num_values, size=final_difference, replace=False)
    values[inds_to_decrement] -= 1

    # failsafe check
    if values.sum() != total_sum:
        raise InternalValueError("Computed random integers do not sum to expected total. Please report to Arthur with "
                                 f"the following debug info: total_sum={total_sum}, num_values={num_values}, "
                                 f"mean_diff_floor={mean_diff_floor}, final_difference={final_difference}, "
                                 f"positive_values={positive_values}, inds_to_decrement={inds_to_decrement}")

    return values


def _parse_duration(time_ref: str) -> timedelta:
    """
    Parses a time duration string. Supports days and hours, e.g. "14d", "-3h", etc.
    :param time_ref: the time string to parse
    :return: timedelta of the parsed value
    """
    raw_value, unit = time_ref[:-1], time_ref[-1:]
    try:
        value = int(raw_value)
    except ValueError as e:
        raise UserValueError(f"Cannot parse time reference value {raw_value}, must be an integer") from e
    if unit == "d":
        return timedelta(days=value)
    elif unit == "h":
        return timedelta(hours=value)
    else:
        raise UserValueError(f"Cannot parse time reference unit {unit}, only days ('d') and hours ('h') are supported")


# for mocking datetime.now without clobbering the entire datetime class
def _datetime_now(*args, **kwargs):
    return datetime.now(*args, **kwargs)


def generate_timestamps(total: int,
                        duration: Union[str, timedelta] = "7d",
                        end: Union[str, datetime] = "now",
                        freq: Union[str, pd.DateOffset] = "D",
                        noisiness: float = 0.3) -> List[datetime]:
    """
    Generates timestamps over a period of time, defaulting to daily timestamps over the last week. Creates `uniques`
    unique timestamp values evenly spaced between `start` and `end` inclusively. Repeats values if
    total ≠ uniques. This is useful for generating timestamps for test inferences outside of a production setting.

    :param total: the total number of timestamps to generate
    :param end: the final timestamp value
    :param duration: the difference between the first and last timestamp values. day or hour strings (e.g. "7d", "4h")
        and timedelta objects are supported
    :param freq: the frequency with which to generate unique values. See
        `Pandas Offset Aliases <https://pandas.pydata.org/docs/user_guide/timeseries.html#offset-aliases>`_ for values
    :param noisiness: how much to noise to add to the number of timestamps repeated at each interval. specifically, the
        coefficient of variation (standard deviation / mean) to use when selecting the number of times to repeat each
        timestamp
    :raises UserValueError: if an input is invalid or values contain future timestamps and allow_future is False
    :return: a list of generated timestamps
    """
    if end == "now":
        end_dt = _datetime_now(pytz.utc)
    elif not isinstance(end, datetime):
        raise UserTypeError(f"'end' should be string 'now' or a datetime object, got type {type(end)} with value {end}")
    else:
        end_dt = end

    if isinstance(duration, str):
        duration = _parse_duration(duration)

    try:
        unique_values = pd.date_range(start=(end_dt - duration), end=end_dt, freq=freq).to_pydatetime()
    except ValueError as e:
        raise UserValueError(e) from e
    unique_count = len(unique_values)

    if unique_count > total:
        raise UserValueError(f"Timestamps with duration {duration} and frequency {freq} yield {unique_count} unique "
                             f"values, but you asked for {total} total values. Total values must be greater than or "
                             "equal to the number of unique timestamps.")

    # determine how many times each timestamp should be repeated
    repeat_counts = normal_random_ints_fixed_sum(unique_count, total, relative_std_dev=noisiness)
    timestamps = unique_values.repeat(repeat_counts).tolist()

    return timestamps


def value_type_to_python_type(value_type: ValueType) -> Type:
    if value_type == ValueType.Integer:
        return int
    elif value_type == ValueType.Float:
        return float
    elif value_type == ValueType.Boolean:
        return bool
    elif value_type in (ValueType.String, ValueType.Unstructured_Text,
                        ValueType.Image):  # image attributes contain strings referencing images
        return str
    elif value_type == ValueType.BoundingBox:
        return list
    else:
        raise UserValueError(f"Can't convert value type {value_type} to Python type")
