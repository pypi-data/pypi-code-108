from typing import List
from typing import Optional
from typing import Tuple

import attr
import pendulum
from pyspark.sql import DataFrame
from pyspark.sql import functions
from pyspark.sql import SparkSession

from tecton_proto.data.new_transformation_pb2 import NewTransformation as Transformation
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource
from tecton_spark.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_spark.partial_aggregations import construct_partial_time_aggregation_df
from tecton_spark.partial_aggregations import TEMPORAL_ANCHOR_COLUMN_NAME
from tecton_spark.pipeline_helper import pipeline_to_dataframe
from tecton_spark.spark_time_utils import convert_timestamp_to_epoch
from tecton_spark.time_utils import convert_timedelta_for_version

MATERIALIZED_RAW_DATA_END_TIME = "_materialized_raw_data_end_time"
TECTON_FEATURE_TIMESTAMP_VALIDATOR = "_tecton_feature_timestamp_validator"


@attr.s(auto_attribs=True)
class MaterializationPlan(object):
    offline_store_data_frame: Optional[DataFrame]
    online_store_data_frame: Optional[DataFrame]
    # should be the most recent ancestor of both online and offline so we can cache both of them easily
    base_data_frame: Optional[DataFrame]
    coalesce: int


def get_batch_materialization_plan(
    *,
    spark: SparkSession,
    feature_definition: FeatureDefinition,
    feature_data_time_limits: Optional[pendulum.Period],
    coalesce: int,
    data_sources: List[VirtualDataSource],
    called_for_online_feature_store: bool = False,
    transformations: Optional[List[Transformation]] = None,
    schedule_interval: Optional[pendulum.Duration] = None,
) -> MaterializationPlan:
    """
    NOTE: We rely on Spark's lazy evaluation model to infer partially materialized tile Schema during FeatureView
    creation time without actually performing any materialization.
    Please make sure to not perform any Spark operations under this function's code path that will actually execute
    the Spark query (e.g: df.count(), df.show(), etc.).
    """

    if feature_definition.is_temporal_aggregate:
        return _get_batch_materialization_plan_for_aggregate_feature_view(
            spark,
            feature_definition,
            False,
            feature_data_time_limits,
            data_sources,
            transformations or [],
            coalesce,
            schedule_interval=schedule_interval,
        )
    elif feature_definition.is_temporal:
        assert feature_data_time_limits is not None
        return _get_batch_materialization_plan_for_temporal_feature_view(
            spark,
            feature_definition,
            False,
            feature_data_time_limits,
            data_sources,
            transformations or [],
            coalesce,
            called_for_online_feature_store,
            schedule_interval=schedule_interval,
        )
    else:
        raise ValueError(f"Unhandled feature view: {feature_definition.fv}")


def _get_batch_materialization_plan_for_aggregate_feature_view(
    spark: SparkSession,
    feature_definition: FeatureDefinition,
    consume_streaming_data_sources: bool,
    feature_data_time_limits: Optional[pendulum.Period],
    data_sources: List[VirtualDataSource],
    transformations: List[Transformation],
    coalesce: int,
    schedule_interval: Optional[pendulum.Duration] = None,
) -> MaterializationPlan:
    df = pipeline_to_dataframe(
        spark,
        feature_definition.fv.pipeline,
        consume_streaming_data_sources,
        data_sources,
        transformations,
        feature_time_limits=feature_data_time_limits,
        schedule_interval=schedule_interval,
    )
    timestamp_key = feature_definition.timestamp_key
    spark_df = _validate_feature_timestamps(spark, df, feature_data_time_limits, timestamp_key)

    trailing_time_window_aggregation = feature_definition.trailing_time_window_aggregation
    online_store_df = offline_store_df = underlying_df = construct_partial_time_aggregation_df(
        spark_df,
        list(feature_definition.join_keys),
        trailing_time_window_aggregation,
        feature_definition.get_feature_store_format_version,
    )

    return MaterializationPlan(offline_store_df, online_store_df, underlying_df, coalesce)


def _get_batch_materialization_plan_for_temporal_feature_view(
    spark: SparkSession,
    feature_definition: FeatureDefinition,
    consume_streaming_data_sources: bool,
    feature_data_time_limits: pendulum.Period,
    data_sources: List[VirtualDataSource],
    transformations: List[Transformation],
    coalesce: int,
    called_for_online_feature_store: bool,
    schedule_interval: Optional[pendulum.Duration] = None,
) -> MaterializationPlan:
    offline_store_df, online_store_df, underlying_df = _materialize_interval_for_temporal_feature_view(
        spark,
        feature_definition,
        feature_data_time_limits,
        data_sources,
        transformations,
        called_for_online_feature_store,
        consume_streaming_data_sources,
        schedule_interval=schedule_interval,
    )

    if called_for_online_feature_store:
        serving_ttl = feature_definition.serving_ttl
        if serving_ttl.in_seconds() > 0:
            online_store_df = _possibly_limit_online_store_df(
                online_store_df, feature_definition.timestamp_key, feature_data_time_limits.end, serving_ttl
            )

    return MaterializationPlan(offline_store_df, online_store_df, underlying_df, coalesce)


def _materialize_interval_for_temporal_feature_view(
    spark: SparkSession,
    fd: FeatureDefinition,
    feature_data_time_limits: pendulum.Period,
    data_sources: List[VirtualDataSource],
    transformations: List[Transformation],
    called_for_online_feature_store: bool,
    consume_streaming_data_sources: bool,
    schedule_interval: Optional[pendulum.Duration] = None,
) -> Tuple[DataFrame, DataFrame, DataFrame]:
    tile_df = pipeline_to_dataframe(
        spark,
        fd.pipeline,
        consume_streaming_data_sources,
        data_sources,
        transformations,
        feature_time_limits=feature_data_time_limits,
        schedule_interval=schedule_interval,
    )

    timestamp_key = fd.timestamp_key
    tile_df = _validate_feature_timestamps(spark, tile_df, feature_data_time_limits, timestamp_key)
    cacheable_df = tile_df

    # We infer partition column (i.e. anchor time) by looking at the feature timestamp column and grouping
    # all the features within `[anchor_time,  anchor_time + batch_schedule)` together.
    version = fd.get_feature_store_format_version
    anchor_time_val = convert_timestamp_to_epoch(functions.col(timestamp_key), version)
    batch_mat_schedule = convert_timedelta_for_version(fd.batch_materialization_schedule, version)
    offline_store_tile_df = tile_df.withColumn(
        TEMPORAL_ANCHOR_COLUMN_NAME, anchor_time_val - anchor_time_val % batch_mat_schedule
    )

    if called_for_online_feature_store:
        # Add raw data end time as a column as it's used for status reporting while writing to Online Feature Store.
        # When materializing multiple tiles, include `raw_data_end_time` per tile so that we can distribute writing
        # to Kafka into multiple partitions.
        online_store_tile_df = offline_store_tile_df.withColumn(
            MATERIALIZED_RAW_DATA_END_TIME, functions.col(TEMPORAL_ANCHOR_COLUMN_NAME) + batch_mat_schedule
        ).drop(TEMPORAL_ANCHOR_COLUMN_NAME)
    else:
        online_store_tile_df = tile_df

    return offline_store_tile_df, online_store_tile_df, cacheable_df


def _validate_feature_timestamps(
    spark: SparkSession,
    feature_df: DataFrame,
    feature_data_time_limits: Optional[pendulum.Period],
    timestamp_key: Optional[str],
) -> DataFrame:
    if feature_data_time_limits:
        # Register the Spark UDF that is contained in the JAR files and that is part of passed Spark session.
        # Jars are included the following way into the Spark session:
        #  - For materialization jobs scheduled by Orchestrator, they are included in the Job submission API.
        #    In this case, we always use the default Spark session of the spun-up Spark cluster.
        #  - For interactive execution (or remote over db-connect / livy), we always construct Spark session
        #    manually and include appropriate JARs ourselves.
        udf_generator = spark.sparkContext._jvm.com.tecton.udfs.spark3.RegisterFeatureTimestampValidator()
        udf_generator.register(TECTON_FEATURE_TIMESTAMP_VALIDATOR)

        start_time_expr = f"to_timestamp('{feature_data_time_limits.start}')"
        # Registered feature timestamp validation UDF checks that each timestamp is within *closed* time interval: [start_time, end_time].
        # So we subtract 1 microsecond here, before passing time limits to the UDF.
        end_time_expr = f"to_timestamp('{feature_data_time_limits.end - pendulum.duration(microseconds=1)}')"
        filter_expr = f"{TECTON_FEATURE_TIMESTAMP_VALIDATOR}({timestamp_key}, {start_time_expr}, {end_time_expr}, '{timestamp_key}')"

        # Force the output of the UDF to be filtered on, so the UDF cannot be optimized away.
        feature_df = feature_df.where(filter_expr)

    return feature_df


def _possibly_limit_online_store_df(
    online_df: DataFrame,
    timestamp_column_name: str,
    feature_end_time: pendulum.DateTime,
    timestamp_range_needed: pendulum.Duration,
) -> DataFrame:
    earliest_timestamp_needed = feature_end_time - timestamp_range_needed
    return online_df.where(functions.col(timestamp_column_name) >= earliest_timestamp_needed)


def get_stream_materialization_plan(
    spark: SparkSession,
    data_sources: List[VirtualDataSource],
    transformations: List[Transformation],
    feature_definition: FeatureDefinition,
) -> MaterializationPlan:
    transformations = transformations or []

    df = None
    if feature_definition:
        df = pipeline_to_dataframe(spark, feature_definition.pipeline, True, data_sources, transformations)
        if feature_definition.is_temporal_aggregate:
            df = construct_partial_time_aggregation_df(
                df,
                list(feature_definition.join_keys),
                feature_definition.trailing_time_window_aggregation,
                feature_definition.get_feature_store_format_version,
            )

    return MaterializationPlan(None, df, df, 0)
