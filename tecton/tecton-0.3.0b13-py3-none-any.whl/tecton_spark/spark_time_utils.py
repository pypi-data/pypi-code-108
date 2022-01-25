import datetime
from typing import Union

import pendulum
from pyspark.sql import Column
from pyspark.sql import functions
from pyspark.sql.functions import expr

from tecton_proto.data.feature_store_pb2 import FeatureStoreFormatVersion
from tecton_spark.time_utils import nanos_to_seconds


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
