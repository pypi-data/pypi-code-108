import datetime
from typing import Union

import pendulum
import pytimeparse
from google.protobuf import duration_pb2
from pyspark.sql import functions
from pyspark.sql.column import Column
from pyspark.sql.functions import expr

from tecton_proto.data.feature_store_pb2 import FeatureStoreFormatVersion
from tecton_spark.errors import TectonValidationError

WINDOW_UNBOUNDED_PRECEDING = "unbounded_preceding"


def timedelta_to_duration(td: datetime.timedelta) -> pendulum.Duration:
    return pendulum.duration(days=td.days, seconds=td.seconds, microseconds=td.microseconds)


def proto_to_duration(proto_duration) -> pendulum.Duration:
    return timedelta_to_duration(proto_duration.ToTimedelta())


def assert_is_round_seconds(d: pendulum.Duration):
    if d % pendulum.Duration(seconds=1):
        raise ValueError(f"{d.in_words()} is not a round number of seconds")
    return d


def assert_valid_time_string(time_str: str, allow_unbounded=False):
    if allow_unbounded:
        if time_str.lower() != WINDOW_UNBOUNDED_PRECEDING and pytimeparse.parse(time_str) is None:
            raise TectonValidationError(
                f"Time string {time_str} must either be `tecton.WINDOW_UNBOUNDED_PRECEDING` or a valid time string."
            )
    else:
        strict_pytimeparse(time_str)


def strict_pytimeparse(time_str: str) -> Union[int, float]:
    parsed = pytimeparse.parse(time_str)
    if parsed is None:
        raise TectonValidationError(f'Could not parse time string "{time_str}"')
    else:
        return parsed


def nanos_to_seconds(nanos: int) -> float:
    """
    :param nanos: Nanoseconds
    :return: Converts nanoseconds to seconds
    """
    return nanos / float(1e9)


def seconds_to_nanos(seconds: int) -> int:
    """
    :param seconds: Seconds
    :return: Converts seconds to nanoseconds
    """
    return int(seconds) * int(1e9)


def subtract_seconds_from_timestamp(
    timestamp: Union[Column, datetime.datetime], delta_seconds: int
) -> Union[Column, datetime.datetime]:
    """
    Subtract seconds from timestamp
    Timestamp can be in Column[Timestamp] or just Timestamp
    :param timestamp: seconds
    :param delta_seconds: seconds
    :return:
    """
    td = datetime.timedelta(seconds=delta_seconds)
    if isinstance(timestamp, Column):
        return timestamp - expr(f"INTERVAL {td.days} DAYS") - expr(f"INTERVAL {td.seconds} SECONDS")
    else:
        return timestamp - td


def add_seconds_to_timestamp(
    timestamp: Union[Column, datetime.datetime], delta_seconds: int
) -> Union[Column, datetime.datetime]:
    """
    Add seconds to timestamp
    Timestamp can be in Column[Timestamp] or just Timestamp
    :param timestamp:  seconds
    :param delta_seconds: seconds
    :return:
    """
    if isinstance(timestamp, Column):
        td = datetime.timedelta(seconds=delta_seconds)
        return timestamp + expr(f"INTERVAL {td.days} DAYS") + expr(f"INTERVAL {td.seconds} SECONDS")
    else:
        td = datetime.timedelta(seconds=delta_seconds)
        return timestamp + td


def convert_timestamp_to_epoch(timestamp: Union[Column, datetime.datetime], version: int) -> Union[Column, int]:
    """
    Convert timestamp to epoch
    Timestamp can be in Column[Timestamp] or just Timestamp
    V0 Return Epoch in seconds
    V1 Return Epoch in nanoseconds
    :param timestamp: Datetime / Datetime column
    :param version: Feature Store Format Version
    :return:
    """
    if version == FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_DEFAULT:
        return get_timestamp_in_seconds(timestamp)
    else:
        return get_timestamp_in_nanos(timestamp)


def convert_epoch_to_datetime(epoch: Union[Column, int], version: int) -> Union[Column, pendulum.datetime]:
    """
    Convert epoch to datetime
    V0 epoch is in seconds
    V1 epoch is in nanoseconds -> convert to seconds
    :param epoch: Epoch based on version
    :param version: Feature Store Format Version
    :return:
    """
    if isinstance(epoch, Column):
        return convert_epoch_to_timestamp_column(epoch, version)
    else:
        epoch_float = float(epoch)
        if version == FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_TIME_NANOSECONDS:
            epoch_float = nanos_to_seconds(epoch)
        return pendulum.from_timestamp(epoch_float)


def get_timestamp_in_seconds(timestamp: Union[Column, datetime.datetime]) -> Union[Column, int]:
    """
    Converts a given timestamp to epoch total seconds
    Timestamp can be in Column[Timestamp] or just Timestamp
    If its a column we need to use a UDF.
    :param timestamp: Datetime / Datetime column
    :return: Timestamp / Timestamp column
    """
    if isinstance(timestamp, Column):
        return timestamp.cast("int")
    else:
        return int(timestamp.timestamp())


def get_timestamp_in_nanos(timestamp: Union[Column, datetime.datetime]) -> Union[Column, int]:
    """
    Converts a given timestamp to epoch total nano seconds
    Timestamp could be a column of timestamp type or
    an actual timestamp. If its a column we need to use
    a UDF.
    :param timestamp: Datetime / Datetime column
    :return: Timestamp / Timestamp column
    """
    if isinstance(timestamp, Column):
        return ((timestamp.cast("double") * 1e6).cast("long")) * 1000
    else:
        return (int(timestamp.timestamp() * 1e6)) * 1000


def convert_epoch_to_timestamp_column(epoch: int, version: int) -> Column:
    """
    Converts an epoch column to a timestamp column
    :param epoch: Epoch Column [V0 : Seconds, V1 : Nanoseconds]
    :param version: Feature Store Format Version
    :return:
    """
    if version == FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_DEFAULT:
        return functions.to_timestamp(epoch)
    else:
        return functions.to_timestamp(epoch / functions.lit(1e9))


def convert_timedelta_for_version(duration: datetime.timedelta, version: int) -> int:
    """
    Convert pendulum duration according to version
    VO -> Return Seconds
    V1 -> Return Nanoseconds
    :param duration: Pendulum Duration
    :param version: Feature Store Format Version
    :return:
    """
    assert duration.microseconds == 0
    interval = duration.total_seconds()
    if version == FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_DEFAULT:
        return int(interval)
    else:
        return int(seconds_to_nanos(interval))


def convert_proto_duration_for_version(duration: duration_pb2.Duration, version: int) -> int:
    return convert_timedelta_for_version(duration.ToTimedelta(), version)


def align_time_downwards(time: datetime.datetime, alignment: datetime.timedelta) -> datetime.datetime:
    excess_seconds = time.timestamp() % alignment.total_seconds()
    return datetime.datetime.utcfromtimestamp(time.timestamp() - excess_seconds)


def align_time_upwards(time: datetime.datetime, alignment: datetime.timedelta) -> datetime.datetime:
    excess_seconds = time.timestamp() % alignment.total_seconds()
    if excess_seconds == 0:
        return time
    return datetime.datetime.utcfromtimestamp(time.timestamp() + alignment.total_seconds() - excess_seconds)
