from typing import List
from typing import Optional
from typing import Tuple

import pendulum
from pyspark.sql import functions
from pyspark.sql import SparkSession
from pyspark.sql.window import Window

from tecton._internals import data_frame_helper
from tecton._internals import errors
from tecton_proto.common import aggregation_function_pb2
from tecton_proto.data.feature_store_pb2 import FeatureStoreFormatVersion
from tecton_proto.data.feature_view_pb2 import TrailingTimeWindowAggregation
from tecton_spark import materialization_plan
from tecton_spark import offline_store
from tecton_spark.aggregation_plans import get_aggregation_plan
from tecton_spark.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_spark.materialization_params import MaterializationParams
from tecton_spark.partial_aggregations import TEMPORAL_ANCHOR_COLUMN_NAME
from tecton_spark.spark_time_utils import convert_epoch_to_datetime
from tecton_spark.spark_time_utils import convert_epoch_to_timestamp_column
from tecton_spark.time_utils import convert_proto_duration_for_version
from tecton_spark.time_utils import convert_timedelta_for_version

"""
This file contains internal methods of feature_views/aggregations.py
Separate file helps de-clutter the main user-visible file.
"""


_TEMPORAL_PREVIEW_DURATION = pendulum.Duration(days=1)


def _get_feature_data_time_limits(fd: FeatureDefinition, spine_time_limits):
    if spine_time_limits is None:
        # If there's no spine, it means we need to preview small portion of the dataframe. So we optimize access from
        # the raw data source by applying artificial time limits to the dataframe
        if fd.is_feature_table:
            time_end = pendulum.now()
            # We choose not to subtract by serving_ttl since it shouldn't be
            # vital for preview functionality and it will improve response
            # times.
            time_start = time_end - _TEMPORAL_PREVIEW_DURATION
            return time_start, time_end
        elif fd.is_temporal or fd.is_temporal_aggregate:
            materialization_params = MaterializationParams.from_feature_definition(fd)
            time_end = materialization_params.most_recent_anchor(pendulum.now("UTC"))
            time_start = time_end
            return time_start, time_end
        elif fd.is_on_demand:
            raise ValueError(f"Invalid invocation on OnDemandFeatureView type for: '{fd.name}'")
        else:
            raise ValueError(f"Unknown feature type for: '{fd.name}'")
    else:
        time_start = spine_time_limits.start
        time_end = spine_time_limits.end

        if fd.is_temporal:
            # Subtract by `serving_ttl` to accommodate for enough feature data for the feature expiration
            serving_ttl = fd.serving_ttl
            time_start = time_start - serving_ttl

        return time_start, time_end


def _align_feature_data_time_limits(
    materialization_params: MaterializationParams, time_start, time_end
) -> Tuple[pendulum.DateTime, pendulum.DateTime]:
    version = materialization_params.feature_definition.get_feature_store_format_version
    time_start = convert_epoch_to_datetime(materialization_params.align_timestamp_left(time_start), version)
    # Since feature data time interval is open on the right, we need to always strictly align right so that
    # with `batch_schedule = 1h`, time end `04:00:00` will be aligned to `05:00:00`.
    time_end = convert_epoch_to_datetime(materialization_params.force_align_timestamp_right(time_end), version)
    return time_start, time_end


def _get_raw_data_time_limits(
    fd: FeatureDefinition, time_start: pendulum.DateTime, time_end: pendulum.DateTime
) -> pendulum.Period:
    if fd.is_temporal_aggregate:
        # Account for final aggregation needing aggregation window prior to earliest timestamp
        max_aggregation_window = fd.max_aggregation_window
        time_start = time_start - max_aggregation_window.ToTimedelta()

    return time_end - time_start


def _get_time_limits(
    fd: FeatureDefinition,
    spine_df,
    spine_time_limits: Optional[pendulum.Period],
):
    """Get the time limits to set on the partially aggregated dataframe."""
    if spine_time_limits is None and spine_df is not None:
        spine_time_limits = data_frame_helper._get_time_limits_of_dataframe(spine_df, fd.timestamp_key)
    time_start, time_end = _get_feature_data_time_limits(fd, spine_time_limits)
    if time_start is None and time_end is None:
        return None

    if not fd.is_feature_table:
        materialization_params = MaterializationParams.from_feature_definition(fd)
        time_start, time_end = _align_feature_data_time_limits(materialization_params, time_start, time_end)

    return _get_raw_data_time_limits(fd, time_start, time_end)


def _get_all_partial_aggregation_tiles_df(
    spark: SparkSession,
    fd: FeatureDefinition,
    use_materialized_data: bool,
    raw_data_time_limits: Optional[pendulum.Period],
    feature_data_time_limits: Optional[pendulum.Period] = None,
):
    """
    Constructs a DF of a partially aggregated data either from materialized or from raw data source with given time limits.
    """

    if not use_materialized_data:
        if feature_data_time_limits is not None:
            _raw_data_time_limits = _get_raw_data_time_limits(
                fd, feature_data_time_limits.start, feature_data_time_limits.end
            )
        else:
            _raw_data_time_limits = raw_data_time_limits

        # TODO(amargvela): For FVs, pass feature data time range here instead of raw data time range
        # cause that's what `get_batch_materialization_plan` expects.
        # This degrades the performance if `window` is large.
        plan = materialization_plan.get_batch_materialization_plan(
            spark=spark,
            feature_definition=fd,
            feature_data_time_limits=_raw_data_time_limits,
            coalesce=10,
            data_sources=fd.data_sources,
            transformations=fd.transformations,
            schedule_interval=fd.batch_materialization_schedule,
        )
        return plan.offline_store_data_frame

    assert fd.materialization_enabled and fd.writes_to_offline_store

    offline_reader_timelimit = raw_data_time_limits
    if feature_data_time_limits is not None:
        offline_reader_timelimit = feature_data_time_limits

    offline_reader = offline_store.get_offline_store_reader(spark, fd)
    return offline_reader.read(offline_reader_timelimit)


def construct_spine_with_all_join_keys_for_TAFV(
    spine_df,
    partial_aggregations_df,
    fd: FeatureDefinition,
    fully_bound_join_keys: List[str],
):
    """
    Appends a spine with wildcard join_key values to result into set of join_keys that should be returned
    by the feature query for BWAFV/SWAFV.

    E.g. Let's say FV has fully bound join_key `A` and wildcard join_key `C`.
    For every row `[a_0, anchor_0]` from the spine, we will have the following rows appended in the
    returned spine:
       [a_0  c_1  anchor_0]
       [a_0  c_2  anchor_0]
        .    .    .
       [a_0  c_k  anchor_0]
    where (`c_1`, ..., `c_k`) represent all the wildcard join_key values such that, the following row is
    present inside `partial_aggregations_df`:
        [a_0, c_i, anchor_i]
    and:
        anchor_0 - max_feature_agg_period < anchor_i <= anchor_0.
    No rows are returned if no `c_i` exists satisfying conditions above.

    :param spine_df: The spine to join against.
    :param partial_aggregations_df: Partially aggregated DataFrame for the FeatureView.
    :param fd: The feature definition
    """
    join_key_conditions = [
        spine_df[join_key] == partial_aggregations_df[join_key] for join_key in fully_bound_join_keys
    ]

    max_aggregation_window = convert_proto_duration_for_version(
        fd.max_aggregation_window, version=fd.get_feature_store_format_version
    )
    join_condition = join_key_conditions + [
        partial_aggregations_df[TEMPORAL_ANCHOR_COLUMN_NAME] <= spine_df[TEMPORAL_ANCHOR_COLUMN_NAME],
        partial_aggregations_df[TEMPORAL_ANCHOR_COLUMN_NAME]
        > spine_df[TEMPORAL_ANCHOR_COLUMN_NAME] - max_aggregation_window,
    ]

    # It is an inner join because, if no wildcard join_key is present in the aggregation window,
    # there should be no features returned for the corresponding set of fully bound join_keys.
    spine_with_all_join_keys = partial_aggregations_df.alias("p").join(spine_df.alias("s"), join_condition, "inner")

    return spine_with_all_join_keys.select(
        [functions.col(f"p.{join_key}").alias(join_key) for join_key in fd.join_keys]
        + [functions.col(f"s.{TEMPORAL_ANCHOR_COLUMN_NAME}").alias(TEMPORAL_ANCHOR_COLUMN_NAME)]
    ).distinct()


def construct_full_tafv_df(
    spark: SparkSession,
    time_aggregation: TrailingTimeWindowAggregation,
    join_keys: List[str],
    feature_store_format_version: FeatureStoreFormatVersion,
    tile_interval: pendulum.Duration,
    fd: FeatureDefinition = None,
    spine_join_keys=None,
    wildcard_join_keys=None,
    spine_df=None,
    all_partial_aggregations_df=None,
    use_materialized_data=True,
    raw_data_time_limits: Optional[pendulum.Period] = None,
    wildcard_key_not_in_spine: bool = False,
):
    """Construct a full time-aggregation data frame from a partial aggregation data frame.

    :param spark: Spark Session
    :param time_aggregation: trailing time window aggregation.
    :param join_keys: join keys to use on the dataframe.
    :param feature_store_format_version: indicates the time precision used by FeatureStore.
    :param tile_interval: Duration of the aggregation tile interval.
    :param fd: Required only if spine_df is provided. The BWAFV/SWAFV object.
    :param spine_df: (Optional) The spine to join against. If present, the returned data frame
        will contain rollups for all (join key, temporal key) combinations that are required
        to compute a full frame from the spine.
    :param all_partial_aggregations_df: (Optional) The full partial
        aggregations data frame to use in place of the a data frame read from the
        materialized parquet tables.
    :param use_materialized_data: (Optional) Use materialized data if materialization is enabled
    :param raw_data_time_limits: (Optional) Spine Time Bounds
    :param wildcard_key_not_in_spine: (Optional) Whether or not the wildcard join_key is present in the spine.
        Defaults to False if spine is not specified or if the FeatureView has no wildcard join_key.
    """
    # TODO: drop anchor time concept from full aggregations. Define start & end times of the aggregation window,
    # use the new concepts for joining, and for returning the temporal aggregate feature dataframes

    if not all_partial_aggregations_df:
        all_partial_aggregations_df = _get_all_partial_aggregation_tiles_df(
            spark, fd, use_materialized_data, raw_data_time_limits
        )
    if wildcard_key_not_in_spine and wildcard_join_keys:
        spine_join_keys.remove(wildcard_join_keys)

    if not spine_df:
        # If spine isn't provided, the fake timestamp equals to anchor time + tile_interval, s.t. the output timestamp
        # completely contains the time range of the fully aggregated window. Note, that ideally we would either subtract
        # 1 second from the timestamp, due to tiles having [start, end) format, or convert tiles in (start, end] format.
        # For now, we're not doing 1 due to it being confusing in preview, and not doing 2 due to it requiring more work
        partial_aggregations_df = all_partial_aggregations_df.withColumn(
            TEMPORAL_ANCHOR_COLUMN_NAME,
            functions.col(TEMPORAL_ANCHOR_COLUMN_NAME)
            + convert_timedelta_for_version(tile_interval, feature_store_format_version),
        )
    else:
        if not fd:
            raise ValueError("fd argument must not be None when spine_df is provided.")
        # TODO: drop anchor column and keep original spine timestamp
        # If spine is provided, round down the time key to the most recent anchor and right join on it + join_keys
        materialization_params = MaterializationParams.from_feature_definition(fd)
        spine_df = spine_df.select(
            materialization_params.most_recent_anchor_time(functions.to_timestamp(time_aggregation.time_key)).alias(
                TEMPORAL_ANCHOR_COLUMN_NAME
            ),
            *spine_join_keys,
        ).distinct()
        # In order to get the training dataframe, we first inner-join all_partial_aggregations_df to spine_df on join keys.
        # This ensures that the resulting df only contains the join keys that we have in spine.
        partial_aggregations_df = all_partial_aggregations_df.join(
            spine_df.select(spine_join_keys).distinct(), spine_join_keys, how="inner"
        )

        if wildcard_key_not_in_spine and wildcard_join_keys:
            # Cache `partial_aggregations_df` as it is used multiple times for joining below
            partial_aggregations_df.cache()

            # If spine does not contain wildcard key, for specific fully bound join_keys and feature timestamp
            # we should find all the values of wildcard join_key that will be present in the feature aggregation
            # window ending at the feature timestamp.
            spine_with_all_join_keys = construct_spine_with_all_join_keys_for_TAFV(
                spine_df,
                partial_aggregations_df,
                fd,
                spine_join_keys,
            )
        else:
            spine_with_all_join_keys = spine_df

        # Make sure the all join keys & anchor times that occur in spine exist in the partially aggregated df
        # This is necessary in the case when the exact anchor time is missing from partially aggregated df,
        # but the previous tiles belonging to the full aggregation window are available. In this case we shouldn't
        # return null, instead we need to aggregate the existing tiles and return the response.
        partial_aggregations_df = partial_aggregations_df.join(
            spine_with_all_join_keys, on=join_keys + [TEMPORAL_ANCHOR_COLUMN_NAME], how="outer"
        )

    aggregations = []
    for feature in time_aggregation.features:
        # We do + 1 since RangeBetween is inclusive, and we do not want to include the last row of the
        # previous tile. See https://github.com/tecton-ai/tecton/pull/1110
        window_duration = pendulum.Duration(seconds=feature.window.ToSeconds())
        upper_range = -(convert_timedelta_for_version(window_duration, feature_store_format_version)) + 1
        window_spec = (
            Window.partitionBy(join_keys)
            .orderBy(functions.col(TEMPORAL_ANCHOR_COLUMN_NAME).asc())
            .rangeBetween(upper_range, 0)
        )
        aggregation_plan = get_aggregation_plan(
            feature.function, feature.function_params, time_aggregation.is_continuous
        )
        names = aggregation_plan.materialized_column_names(feature.input_feature_name)
        input_columns = [functions.col(name) for name in names]

        if feature.function == aggregation_function_pb2.AGGREGATION_FUNCTION_LASTN:
            # There isn't an Scala Encoder that works with a list directly, so instead we wrap the list in an object. Here we
            # strip the object to get just the list.
            aggregations.append(
                aggregation_plan.full_aggregation_transform(names[0], window_spec).values.alias(
                    feature.output_feature_name
                )
            )
        else:
            aggregations.append(
                aggregation_plan.full_aggregation_transform(input_columns, window_spec).alias(
                    feature.output_feature_name
                )
            )

    output_df = partial_aggregations_df.select(join_keys + [TEMPORAL_ANCHOR_COLUMN_NAME] + aggregations)
    if spine_df:
        output_df = output_df.join(spine_df, on=spine_join_keys + [TEMPORAL_ANCHOR_COLUMN_NAME], how="inner")
    output_df = output_df.withColumn(
        TEMPORAL_ANCHOR_COLUMN_NAME,
        convert_epoch_to_timestamp_column(functions.col(TEMPORAL_ANCHOR_COLUMN_NAME), feature_store_format_version),
    )
    return output_df.withColumnRenamed(TEMPORAL_ANCHOR_COLUMN_NAME, time_aggregation.time_key)


def construct_spine_with_all_join_keys_for_TFV(
    spine_df, tile_df, timestamp_column: str, serving_ttl: int, fully_bound_join_keys: List[str], join_keys: List[str]
):
    """
     Appends a spine with wildcard join_key values to result into set of join_keys that should be returned
     by the feature query for BFV/SFV.

     E.g. Let's say FV has fully bound join_key `A` and wildcard join_key `C`.
     For every row `[a_0, feature_ts_0]` from the spine, we will have the following rows appended in the
     returned spine:
        [a_0  c_1  feature_ts_1]
        [a_0  c_2  feature_ts_2]
         .    .    .
        [a_0  c_k  feature_ts_k]
    where (`c_1`, ..., `c_k`) represent all the wildcard join_key values such that, the following row is
    present inside `tile_df`:
        [a_0, c_i, feature_ts_i]
    and:
        feature_ts_0 - serving_ttl < feature_ts_i <= feature_ts_0.

     :param spine_df: The spine to join against.
     :param tile_df: Partially aggregated DataFrame for the FeatureView.
    """

    join_key_conditions = [spine_df[join_key] == tile_df[join_key] for join_key in fully_bound_join_keys]

    join_condition = join_key_conditions + [
        tile_df[timestamp_column] <= spine_df[timestamp_column],
        tile_df[timestamp_column]
        > functions.from_unixtime(functions.unix_timestamp(spine_df[timestamp_column]) - serving_ttl),
    ]

    # It is an inner join because, if no wildcard join_key is present prior to requested timestamp,
    # there should be no features returned for the corresponding set of fully bound join_keys.
    spine_with_all_join_keys = tile_df.alias("t").join(spine_df.alias("s"), join_condition, "inner")

    return spine_with_all_join_keys.select(
        [functions.col(f"t.{join_key}").alias(join_key) for join_key in join_keys]
        + [functions.col(f"s.{timestamp_column}").alias(timestamp_column)]
    ).distinct()


def construct_full_tfv_or_ft_df(
    spark: SparkSession,
    fd: FeatureDefinition,
    spine_df=None,
    all_tiles_df=None,
    use_materialized_data=True,
    raw_data_time_limits: Optional[pendulum.Period] = None,
    wildcard_key_not_in_spine: bool = False,
):
    """Construct a full data frame from a partial aggregation data frame.

    :param spine_df: (Optional) The spine to join against. If present, the returned data frame
        will contain rollups for all join key combinations that are required
        to compute a full frame from the spine.
    :param all_tiles_df: (Optional) The tile data frame to use in place of the a data frame read from the
        materialized parquet tables.
    :param use_materialized_data: (Optional) Use materialized data if materialization is enabled
    :param raw_data_time_limits: (Optional) Spine Time Bounds
    :param wildcard_key_not_in_spine: Whether or not the wildcard join_key is present in the spine.
        Defaults to False if spine is not specified or if the feature definition has no wildcard join_key.
    """
    if not fd.is_temporal and not fd.is_feature_table:
        raise ValueError(f"Invalid invocation on non BFV/SFV/FeatureTable type for: '{fd.name}'")

    timestamp_key = fd.timestamp_key

    # Currently we only support fetching pre-materialized data. In the future we may do
    # fetching from the raw data, or do a hybrid where we materialize dynamically for the missing data
    if not all_tiles_df:
        all_tiles_df = _get_all_partial_aggregation_tiles_df(spark, fd, use_materialized_data, raw_data_time_limits)

    all_join_keys = fd.join_keys + [timestamp_key]
    if not spine_df:
        # For preview we just need to return DataFrame as it is, except we need to drop the unnecessary anchor time
        return all_tiles_df.select(all_join_keys + fd.features)

    wildcard_join_key = fd.wildcard_join_key
    spine_join_keys = fd.join_keys
    if wildcard_key_not_in_spine and wildcard_join_key:
        spine_join_keys.remove(wildcard_join_key)

    # In order to get the training dataframe, we first inner-join all_tiles_df to spine_df on join keys.
    # This ensures that the resulting df only contains the join keys that we have in spine.
    tiles_df = all_tiles_df.join(spine_df.select(spine_join_keys).distinct(), spine_join_keys, how="inner")
    if wildcard_key_not_in_spine and wildcard_join_key:
        # Cache `tiles_df` as it is used multiple times for joining below
        tiles_df.cache()

        # If spine does not contain wildcard key, for specific fully bound join_keys and feature timestamp
        # we should find all the values of wildcard join_key that will be present in the pre-materialized
        # features with a feature timestamp less than feature timestamp from the spine (to avoid data leakeage).
        serving_ttl = int(fd.serving_ttl.total_seconds())
        timestamp_column = fd.timestamp_key
        spine_with_all_join_keys = construct_spine_with_all_join_keys_for_TFV(
            spine_df, tiles_df, timestamp_column, serving_ttl, spine_join_keys, fd.join_keys
        )
    else:
        spine_with_all_join_keys = spine_df.select(all_join_keys).drop_duplicates()

    # Next, we do an outer join of tiles_df & spine_df on join_keys + timestamp columns. This ensures that
    # rows from spine_df are inserted into df with NULL feature values
    # (except if the timestamps exactly match we'll not have NULL feature value).
    tiles_df = tiles_df.join(spine_with_all_join_keys, all_join_keys, how="outer")
    # Next, we run the "last" window function with (-serving_ttl, 0) window while partitioning the data on fv.join_keys.
    # Since the "last" function is run with ignorenulls=True parameter, it'll fill in the feature values of rows originating
    # from spine_df with previous values, which is exactly what we want (fuzzy join on closest earlier event).
    serving_ttl = int(fd.serving_ttl.total_seconds())
    # We want features with timestamp exactly `serving_ttl` ago not to be included, so we pass
    # `-serving_ttl + 1` in a `rangeBetween` clause below.
    window_spec = (
        Window.partitionBy(fd.join_keys)
        .orderBy(functions.col(timestamp_key).cast("long").asc())
        .rangeBetween(-serving_ttl + 1, 0)
    )

    aggregations = []
    for column_name in fd.features:
        aggregations.append(functions.last(column_name, ignorenulls=True).over(window_spec).alias(column_name))

    df = tiles_df.select(all_join_keys + aggregations)
    # Finally, we right-join df with spine_df on fully_bound_join_keys + timestamp, so that we return only the
    # rows that were needed by the user.
    final_joining_keys = spine_join_keys + [timestamp_key]
    df = df.join(spine_df.select(final_joining_keys).distinct(), final_joining_keys, how="right").drop_duplicates()
    return df


def get_all_temporal_ft_features(
    spark: SparkSession,
    fd: FeatureDefinition,
    entities=None,
    use_materialized_data=True,
    feature_data_time_limits: Optional[pendulum.Period] = None,
):
    assert (
        fd.is_temporal or fd.is_feature_table
    ), f"Invalid invocation on non BFV/SFV/FeatureTable type for: '{fd.name}'"

    if not use_materialized_data and fd.is_feature_table:
        raise errors.FT_UNABLE_TO_ACCESS_SOURCE_DATA(fd.name)

    df = _get_all_partial_aggregation_tiles_df(
        spark, fd, use_materialized_data, None, feature_data_time_limits=feature_data_time_limits
    )

    if entities is not None:
        df = df.join(entities.distinct(), on=entities.columns, how="right")

    columns = fd.join_keys + fd.features + [fd.timestamp_key]
    return df.select(*columns)
