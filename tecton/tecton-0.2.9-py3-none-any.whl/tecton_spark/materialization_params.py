import datetime
from typing import List

import pendulum
from pyspark.sql.types import *

from tecton_spark import time_utils
from tecton_spark.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_spark.time_utils import convert_epoch_to_datetime
from tecton_spark.time_utils import convert_timedelta_for_version
from tecton_spark.time_utils import convert_timestamp_to_epoch
from tecton_spark.time_utils import subtract_seconds_from_timestamp

DIAGNOSTIC_DATE_FORMAT = "%Y-%m-%d %H:%M:%S %Z"


class MaterializationParams(object):
    """
    Holds the configuration for scheduled materializations.
    """

    def __init__(
        self,
        min_scheduling_interval: pendulum.Duration,
        allowed_upstream_lateness: pendulum.Duration,
        from_timestamp: pendulum.datetime,
        batch_schedule: pendulum.Duration = pendulum.Duration(),
        data_partitions_coalesce_override: int = None,
        feature_definition: FeatureDefinition = None,
        **kwargs,
    ):
        """
        :param min_scheduling_interval: Minimum scheduling time interval.
        :param batch_schedule: Batch materialization schedule
        :param allowed_upstream_lateness: The materialization run that
            consumes an event with timestamp T will not run until after
            this time after T.
        :param from_timestamp: No materialization runs will be scheduled with
            an anchor before this time.
        :param data_partitions_coalesce_override: Override the number of partitions in the materialized data (on top of tiles).
        """
        self.feature_definition = feature_definition
        self.min_scheduling_interval = time_utils.assert_is_round_seconds(min_scheduling_interval)
        self.batch_schedule = time_utils.assert_is_round_seconds(batch_schedule)
        self.allowed_upstream_lateness = time_utils.assert_is_round_seconds(allowed_upstream_lateness)
        self.from_timestamp = from_timestamp
        self.data_partitions_coalesce_override = data_partitions_coalesce_override

    @staticmethod
    def from_feature_definition(feature_definition: FeatureDefinition):
        return MaterializationParams(
            feature_definition=feature_definition,
            min_scheduling_interval=feature_definition.min_scheduling_interval,
            batch_schedule=feature_definition.batch_materialization_schedule,
            allowed_upstream_lateness=feature_definition.allowed_upstream_lateness,
            from_timestamp=feature_definition.start_timestamp,
            data_partitions_coalesce_override=feature_definition.data_partitions_coalesce_override,
        )

    def __str__(self):
        lines = [
            f"Batch Materialization Schedule: {self.batch_schedule.in_words()}",
            f"Start Time: {self.from_timestamp.strftime(DIAGNOSTIC_DATE_FORMAT)}",
            f"Schedule Offset: {self.allowed_upstream_lateness_words()}",
        ]
        return "\n".join(lines)

    def allowed_upstream_lateness_words(self):
        in_words = self.allowed_upstream_lateness.in_words()
        # in_words() returns '' for a duration of zero
        return in_words if in_words is not "" else "0 seconds"

    def get_tile_interval(self):
        return time_utils.assert_is_round_seconds(self.feature_definition.get_tile_interval)

    def most_recent_anchor(self, timestamp: pendulum.datetime) -> pendulum.datetime:
        """Computes the most recent anchor time which is ready to be computed.

        :param timestamp: The timestamp.
        :return: The timestamp of the greatest ready anchor time <= timestamp.
        """
        anchor_time = self.most_recent_anchor_time(timestamp)
        return convert_epoch_to_datetime(anchor_time, self.feature_definition.get_feature_store_format_version)

    def most_recent_anchor_time(self, timestamp: datetime.datetime) -> int:
        """Computes the most recent anchor time which is ready to be computed.

        :param timestamp: The timestamp in python date time
        :return: The timestamp in seconds of the greatest ready anchor time <= timestamp.
        """
        return self.most_recent_tile_end_time(
            subtract_seconds_from_timestamp(timestamp, self.min_scheduling_interval.in_seconds())
        )

    def most_recent_tile_end_time(self, timestamp: datetime.datetime) -> int:
        """Computes the most recent tile end time which is ready to be computed.

        :param timestamp: The timestamp in python datetime format
        :return: The timestamp in seconds of the greatest ready tile end time <= timestamp.
        """
        return self.align_timestamp_left(
            subtract_seconds_from_timestamp(timestamp, self.allowed_upstream_lateness.in_seconds())
        )

    def align(self, timestamp: pendulum.datetime) -> pendulum.datetime:
        """Aligns a time to this schedule.

        This function does not take allowed lateness into account.

        :param timestamp: The timestamp to align.
        :return: The timestamp of the greatest aligned time <= timestamp.
        """
        aligned_time = self.align_timestamp_left(timestamp)
        return convert_epoch_to_datetime(aligned_time, self.feature_definition.get_feature_store_format_version)

    def align_timestamp_left(self, timestamp: datetime.datetime) -> int:
        """Aligns a time to this schedule.

        This function does not take allowed lateness into account.

        :param timestamp: The timestamp in python datetime format
        :return: The timestamp of the greatest aligned time <= timestamp, in seconds.
        """
        is_continuous_aggregate = (
            self.feature_definition.is_temporal_aggregate and self.feature_definition.is_continuous_temporal_aggregate
        )
        if not self.min_scheduling_interval and not is_continuous_aggregate:
            raise Exception(f"Interval must be greater than 0; got {self.min_scheduling_interval}")

        version = self.feature_definition.get_feature_store_format_version
        scheduling_interval = convert_timedelta_for_version(self.min_scheduling_interval, version)
        timestamp_epoch = convert_timestamp_to_epoch(timestamp, version)
        aligning_delta = 0
        if scheduling_interval > 0:
            aligning_delta = timestamp_epoch % scheduling_interval

        return timestamp_epoch - aligning_delta

    def force_align_timestamp_right(self, timestamp: datetime.datetime) -> int:
        """Aligns timestamp to the scheduling interval. If it's already aligned,
        adds scheduling interval's length.

        This function does not take allowed lateness into account.

        :param timestamp: The timestamp in python datetime format
        :return: The timestamp of the greatest aligned time <= timestamp, in seconds.
        """
        aligned_left = self.align_timestamp_left(timestamp)

        version = self.feature_definition.get_feature_store_format_version
        scheduling_interval = convert_timedelta_for_version(self.min_scheduling_interval, version)

        return aligned_left + scheduling_interval

    def align_timestamp_right(self, timestamp: datetime.datetime) -> int:
        """Aligns a time to this schedule.

        :param timestamp: The timestamp in python datetime format
        :return: The timestamp of the lowest aligned time >= timestamp, in seconds.
        """
        is_continuous_aggregate = (
            self.feature_definition.is_temporal_aggregate and self.feature_definition.is_continuous_temporal_aggregate
        )
        if not self.min_scheduling_interval and not is_continuous_aggregate:
            raise Exception(f"Interval must be greater than 0; got {self.min_scheduling_interval}")

        version = self.feature_definition.get_feature_store_format_version
        scheduling_interval = convert_timedelta_for_version(self.min_scheduling_interval, version)
        timestamp_epoch = convert_timestamp_to_epoch(timestamp, version)
        aligning_delta = 0
        if scheduling_interval > 0:
            aligning_delta = timestamp_epoch % scheduling_interval

        timestamp_epoch = timestamp_epoch + scheduling_interval - aligning_delta
        return timestamp_epoch

    def construct_anchor_times(self, start_time, num_tiles, version) -> List[int]:
        """Creates `num_tiles` consecutive anchor_times starting from `start_time`.

        :return: An increasing list of consecutive anchor times.
        """
        anchor_times = []
        for i in range(num_tiles):
            anchor_time = start_time + i * self.get_tile_interval()
            anchor_time_val = convert_timestamp_to_epoch(anchor_time, version)
            anchor_times.append(anchor_time_val)

        return anchor_times

    @staticmethod
    def time_range(start_time, end_time) -> pendulum.Period:
        return pendulum.instance(end_time) - pendulum.instance(start_time)

    def construct_tile_end_times(self, latest_tile_end_time, num_tiles, version) -> List[int]:
        """Creates `num_tiles` consecutive tile_end_times where latest one ends at `latest_tile_end_time`.

        :return: An increasing list of consecutive tile end times.
        """
        tile_end_times = []
        for i in range(num_tiles):
            tile_end_time = latest_tile_end_time - i * self.batch_schedule
            time_val = convert_timestamp_to_epoch(tile_end_time, version)
            tile_end_times.append(time_val)

        tile_end_times.reverse()
        return tile_end_times
