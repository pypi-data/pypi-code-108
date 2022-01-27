from typing import List

from pyspark.sql import DataFrame
from pyspark.sql import functions

from tecton_proto.data.feature_view_pb2 import TrailingTimeWindowAggregation
from tecton_spark.aggregation_plans import get_aggregation_plan
from tecton_spark.aggregation_utils import get_aggregation_column_prefix_from_column_name
from tecton_spark.aggregation_utils import get_aggregation_column_prefixes
from tecton_spark.aggregation_utils import get_continuous_aggregation_value
from tecton_spark.spark_helper import is_spark3
from tecton_spark.time_utils import convert_timestamp_to_epoch

TEMPORAL_ANCHOR_COLUMN_NAME = "_anchor_time"
WINDOW_COLUMN_NAME = "window"


def _get_feature_partial_aggregations(aggregation_plan, feature_name: str):
    column_names = set()
    for column_name, aggregated_column in zip(
        aggregation_plan.materialized_column_names(feature_name),
        aggregation_plan.partial_aggregation_transform(feature_name),
    ):
        if column_name in column_names:
            continue
        column_names.add(column_name)

        yield column_name, aggregated_column.alias(column_name)


def _convert_window_to_anchor_time(
    output_df,
    is_continuous,
    time_key,
    version,
    window_start_column_name,
    window_end_column_name,
    convert_window_times_to_epoch,
):
    def _add_time_column(df, input_ts_column_name, output_column_name):
        col = functions.col(input_ts_column_name)
        return df.withColumn(
            output_column_name, convert_timestamp_to_epoch(col, version) if convert_window_times_to_epoch else col
        )

    # For continuous aggregations this will simply be the time key.
    if is_continuous:
        return _add_time_column(output_df, time_key, TEMPORAL_ANCHOR_COLUMN_NAME)

    # Grouping by Spark Window introduces the "window" struct with "start" and "end" columns.
    # We only need to keep the "start" column as an anchor time.
    anchor_column_name = window_start_column_name if window_start_column_name else TEMPORAL_ANCHOR_COLUMN_NAME
    output_df = _add_time_column(output_df, f"{WINDOW_COLUMN_NAME}.start", anchor_column_name)

    if window_end_column_name:
        output_df = _add_time_column(output_df, f"{WINDOW_COLUMN_NAME}.end", window_end_column_name)

    return output_df.drop(WINDOW_COLUMN_NAME)


def construct_partial_time_aggregation_df(
    df,
    join_keys: List[str],
    time_aggregation: TrailingTimeWindowAggregation,
    version,
    window_start_column_name: str = None,
    window_end_column_name: str = None,
    convert_to_epoch: bool = True,
):
    output_columns = set()
    if not time_aggregation.is_continuous:
        group_by_cols = [functions.col(join_key) for join_key in join_keys]
        slide_str = f"{time_aggregation.aggregation_slide_period.seconds} seconds"
        window_spec = functions.window(time_aggregation.time_key, slide_str, slide_str)
        group_by_cols = [window_spec] + group_by_cols
        aggregations = []
        for feature in time_aggregation.features:
            aggregation_plan = get_aggregation_plan(
                feature.function, feature.function_params, time_aggregation.is_continuous
            )
            for name, aggregation in _get_feature_partial_aggregations(aggregation_plan, feature.input_feature_name):
                if name in output_columns:
                    continue
                output_columns.add(name)
                aggregations.append(aggregation)
        output_df = df.groupBy(*group_by_cols).agg(*aggregations)
        if is_spark3():
            # There isn't an Scala Encoder that works with a list directly, so instead we wrap the list in an object. Here
            # we strip the object to get just the list.
            for col_name in output_columns:
                if col_name.startswith("lastn"):
                    output_df = output_df.withColumn(col_name, output_df[col_name].values)
    else:
        columns_to_drop = set()
        for feature in time_aggregation.features:
            column_prefixes = get_aggregation_column_prefixes(feature.function)
            for column_prefix in column_prefixes:
                full_name = f"{column_prefix}_{feature.input_feature_name}"
                if full_name in output_columns:
                    continue
                output_columns.add(full_name)
                df = df.withColumn(
                    full_name, get_continuous_aggregation_value(column_prefix, feature.input_feature_name)
                )
            columns_to_drop.add(feature.input_feature_name)
        # Drop the original feature columns.
        for column in columns_to_drop:
            df = df.drop(column)
        output_df = df

    output_df = _convert_window_to_anchor_time(
        output_df,
        time_aggregation.is_continuous,
        time_aggregation.time_key,
        version,
        window_start_column_name,
        window_end_column_name,
        convert_to_epoch,
    )
    return output_df


def rename_partial_aggregate_columns(
    df: DataFrame, slide_interval_string: str, trailing_time_window_aggregation: TrailingTimeWindowAggregation
) -> DataFrame:
    """Rename partial aggregate columns to human readable format."""
    # Create a map from intermediate rollup column name to preferred column names.
    renaming_map = dict()
    for feature in trailing_time_window_aggregation.features:
        aggregation_plan = get_aggregation_plan(
            feature.function, feature.function_params, trailing_time_window_aggregation.is_continuous
        )
        for old_name in aggregation_plan.materialized_column_names(feature.input_feature_name):
            aggregation_function_name = get_aggregation_column_prefix_from_column_name(feature.function, old_name)
            renaming_map[old_name] = f"{feature.input_feature_name}_{aggregation_function_name}_{slide_interval_string}"
    for (old_name, new_name) in renaming_map.items():
        df = df.withColumnRenamed(old_name, new_name)
    return df
