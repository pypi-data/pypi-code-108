from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union

import pandas
import pendulum
import sqlparse

from tecton_proto.common import aggregation_function_pb2 as afpb
from tecton_proto.data.feature_view_pb2 import FeatureView as FeatureViewProto
from tecton_proto.data.feature_view_pb2 import NewTemporalAggregate
from tecton_spark import time_utils
from tecton_spark.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_spark.feature_set_config import FeatureSetConfig
from tecton_spark.snowflake.errors import TectonSnowflakeNotImplementedError
from tecton_spark.snowflake.pipeline_helper import pipeline_to_df_with_input
from tecton_spark.snowflake.pipeline_helper import pipeline_to_df_with_mock_input
from tecton_spark.snowflake.pipeline_helper import pipeline_to_sql_string
from tecton_spark.snowflake.templates_utils import load_template

TEMP_SPINE_TABLE_NAME = "_TEMP_SPINE_TABLE_FROM_DF"

HISTORICAL_FEATURES_TEMPLATE = None
MATERIALIZATION_TILE_TEMPLATE = None
MATERIALIZATION_TEMPLATE = None
TIME_LIMIT_TEMPLATE = None
FULL_AGGREGATION_TEMPLATE = None
PARTIAL_AGGREGATION_TEMPLATE = None

# TODO(TEC-6204): Last and LastN are not currently supported
#
# Map of proto function type -> set of (output column prefix, snowflake function name)
AGGREGATION_PLANS = {
    afpb.AGGREGATION_FUNCTION_SUM: {("SUM", "SUM")},
    afpb.AGGREGATION_FUNCTION_MIN: {("MIN", "MIN")},
    afpb.AGGREGATION_FUNCTION_MAX: {("MAX", "MAX")},
    afpb.AGGREGATION_FUNCTION_COUNT: {("COUNT", "COUNT")},
    afpb.AGGREGATION_FUNCTION_MEAN: {("COUNT", "COUNT"), ("MEAN", "AVG")},
}


def _load_template():
    # TODO: Do this at module loading time once we sort out including the templates in the public SDK build
    global HISTORICAL_FEATURES_TEMPLATE
    if not HISTORICAL_FEATURES_TEMPLATE:
        HISTORICAL_FEATURES_TEMPLATE = load_template("historical_features.sql.j2")
    global MATERIALIZATION_TILE_TEMPLATE
    if not MATERIALIZATION_TILE_TEMPLATE:
        MATERIALIZATION_TILE_TEMPLATE = load_template("materialization_tile.sql.j2")
    global MATERIALIZATION_TEMPLATE
    if not MATERIALIZATION_TEMPLATE:
        MATERIALIZATION_TEMPLATE = load_template("materialization.sql.j2")
    global TIME_LIMIT_TEMPLATE
    if not TIME_LIMIT_TEMPLATE:
        TIME_LIMIT_TEMPLATE = load_template("time_limit.sql.j2")
    global FULL_AGGREGATION_TEMPLATE
    if not FULL_AGGREGATION_TEMPLATE:
        FULL_AGGREGATION_TEMPLATE = load_template("run_full_aggregation.sql.j2")
    global PARTIAL_AGGREGATION_TEMPLATE
    if not PARTIAL_AGGREGATION_TEMPLATE:
        PARTIAL_AGGREGATION_TEMPLATE = load_template("run_partial_aggregation.sql.j2")


def _format_sql(sql_str: str) -> str:
    return sqlparse.format(sql_str, reindent=True, keyword_case="upper")


@dataclass
class _FeatureSetItemInput:
    """A simplified version of FeatureSetItem which is passed to the SQL template."""

    name: str
    timestamp_key: str
    join_keys: Dict[str, str]
    features: List[str]
    sql: str
    aggregation: Optional[NewTemporalAggregate]
    ttl_seconds: Optional[int]


def get_historical_features(
    spine: Union[pandas.DataFrame, str, "snowflake.snowpark.DataFrame"],
    session: "snowflake.snowpark.Session",
    feature_set_config: FeatureSetConfig,
    timestamp_key: str,
    include_feature_view_timestamp_columns: bool = False,
    # Whether to use the registered snowflake view for features.
    from_registered_view: bool = True,
) -> "snowflake.snowpark.DataFrame":
    from snowflake.snowpark import DataFrame

    _load_template()
    if include_feature_view_timestamp_columns:
        # TODO(TEC-7238): Implement this
        raise TectonSnowflakeNotImplementedError(
            "include_feature_view_timestamp_columns is not implemented for Snowflake"
        )
    if isinstance(spine, str):
        spine_sql = spine
    elif isinstance(spine, DataFrame):
        _create_temp_table_for_df(session=session, df=spine, table_name=TEMP_SPINE_TABLE_NAME)
        spine.write.mode("append").saveAsTable(TEMP_SPINE_TABLE_NAME)
        spine_sql = f"SELECT * FROM {TEMP_SPINE_TABLE_NAME}"
    elif isinstance(spine, pandas.DataFrame):
        # TODO: Use write_pandas once snowflake support to create a temp table with it.
        spine_df = session.createDataFrame(spine)

        _create_temp_table_for_df(session=session, df=spine_df, table_name=TEMP_SPINE_TABLE_NAME)
        spine_df.write.mode("append").saveAsTable(TEMP_SPINE_TABLE_NAME)
        spine_sql = f"SELECT * FROM {TEMP_SPINE_TABLE_NAME}"

    feature_set_items = feature_set_config._get_feature_definitions_and_join_configs()
    input_items = []
    for item in feature_set_items:
        fd = item.feature_definition
        feature_view = fd.fv
        # Change the feature view name if it's for internal udf use.
        if item.namespace.startswith("_udf_internal"):
            name = item.namespace.upper()
        else:
            name = fd.name

        if not fd.is_on_demand:
            join_keys = {key: value for key, value in item.join_keys}
            features = [
                col_name
                for col_name in fd.view_schema.column_names()
                if col_name not in (list(join_keys.keys()) + [fd.timestamp_key])
            ]
            if len(fd.online_serving_index.join_keys) != len(fd.join_keys):
                raise TectonSnowflakeNotImplementedError("Wildcard is not supported for Snowflake")
            if from_registered_view:
                source = f"SELECT * FROM {feature_view.snowflake_data.snowflake_view_name}"
            else:
                source = pipeline_to_sql_string(
                    pipeline=fd.pipeline,
                    data_sources=fd.data_sources,
                    transformations=fd.transformations,
                )
            sql_str = TIME_LIMIT_TEMPLATE.render(
                source=source,
                timestamp_key=fd.timestamp_key,
                # Apply time limit from feature_start_time
                start_time=fd.start_timestamp,
            )
            input_items.append(
                _FeatureSetItemInput(
                    name=name,
                    timestamp_key=fd.timestamp_key,
                    join_keys=join_keys,
                    features=features,
                    sql=sql_str,
                    aggregation=(
                        feature_view.temporal_aggregate if feature_view.HasField("temporal_aggregate") else None
                    ),
                    ttl_seconds=(int(fd.serving_ttl.total_seconds()) if fd.is_temporal else None),
                )
            )
    sql_str = HISTORICAL_FEATURES_TEMPLATE.render(
        feature_set_items=input_items,
        spine_timestamp_key=timestamp_key,
        spine_sql=spine_sql,
        include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
    )
    output_df = session.sql(sql_str)

    # Apply ODFV to the spine
    for item in feature_set_items:
        fd = item.feature_definition
        feature_view = fd.fv
        if fd.is_on_demand:
            view_schema = fd.view_schema
            schema_dict = {col_name: view_schema.spark_type(col_name) for col_name in view_schema.column_names()}
            output_df = pipeline_to_df_with_input(
                session=session,
                input_df=output_df,
                pipeline=fd.pipeline,
                transformations=fd.transformations,
                output_schema=schema_dict,
                name=fd.name,
                fv_id=fd.id,
            )
    columns_to_drop = [column for column in output_df.columns if "_UDF_INTERNAL_" in column]
    if len(columns_to_drop) > 0:
        output_df = output_df.drop(*columns_to_drop)
    return output_df


def _create_temp_table_for_df(
    session: "snowflake.snowpark.Session", table_name: str, df: "snowflake.snowpark.DataFrame"
):
    """
    Create a temporary table for the given dataframe.
    """
    # TODO: This implementation uses some internal snowflake APIs, we should replace this when they
    # have official support for our use case.
    from snowflake.snowpark._internal.analyzer.analyzer_package import AnalyzerPackage
    from snowflake.snowpark._internal.analyzer.sf_attribute import Attribute

    attributes = [Attribute(f.name, f.datatype, f.nullable) for f in df.schema.fields]
    pkg = AnalyzerPackage()
    schema_string = pkg.attribute_to_schema_string(attributes)
    create_tmp_table_sql = f"CREATE OR REPLACE TEMPORARY TABLE {table_name} ({schema_string})"
    session.sql(create_tmp_table_sql).collect()


def run_batch(
    session: "snowflake.snowpark.Session",
    feature_view: FeatureViewProto,
    # start is inclusive and end is exclusive
    feature_start_time: Union[pendulum.DateTime, datetime] = None,
    feature_end_time: Union[pendulum.DateTime, datetime] = None,
    aggregation_level: str = "full",
) -> "snowflake.snowpark.DataFrame":
    # Smart default feature_start_time and feature_end_time if unset.
    if feature_end_time is None:
        feature_end_time = pendulum.now()
    if feature_start_time is None:
        schedule_interval = time_utils.proto_to_duration(feature_view.materialization_params.schedule_interval)
        feature_start_time = feature_end_time - schedule_interval
    if feature_view.HasField("temporal_aggregate"):
        if aggregation_level == "full":
            aggregated_tiles_sql_str = get_materialization_sql_str(
                feature_view=feature_view,
                time_limits=pendulum.period(feature_start_time, feature_end_time),
            )
            aggregated_sql_str = FULL_AGGREGATION_TEMPLATE.render(
                source=aggregated_tiles_sql_str,
                join_keys=list(feature_view.join_keys),
                aggregation=feature_view.temporal_aggregate,
                timestamp_key=feature_view.timestamp_key,
                name=feature_view.fco_metadata.name,
            )
            return session.sql(_format_sql(aggregated_sql_str))
        elif aggregation_level == "partial":
            aggregated_tiles_sql_str = get_materialization_sql_str(
                feature_view=feature_view,
                time_limits=pendulum.period(feature_start_time, feature_end_time),
            )
            # Rename the output columns, and add tile start/end time columns
            partial_aggregated_sql_str = PARTIAL_AGGREGATION_TEMPLATE.render(
                source=aggregated_tiles_sql_str,
                join_keys=list(feature_view.join_keys),
                aggregations=_get_feature_view_aggregations(feature_view),
                slide_interval=feature_view.temporal_aggregate.slide_interval,
                slide_interval_string=feature_view.temporal_aggregate.slide_interval_string,
                timestamp_key=feature_view.timestamp_key,
            )
            return session.sql(_format_sql(partial_aggregated_sql_str))
        elif aggregation_level == "disabled":
            sql_str = TIME_LIMIT_TEMPLATE.render(
                source=feature_view.snowflake_data.snowflake_view_name,
                timestamp_key=feature_view.timestamp_key,
                start_time=feature_start_time,
                end_time=feature_end_time,
            )
            return session.sql(_format_sql(sql_str))
        else:
            raise ValueError(f"Unsupported aggregation level: {aggregation_level}")

    else:
        sql_str = get_materialization_sql_str(
            feature_view=feature_view,
            time_limits=pendulum.period(feature_start_time, feature_end_time),
        )
        return session.sql(_format_sql(sql_str))


def run_ondemand(
    session: "snowflake.snowpark.Session", fd: FeatureDefinition, mock_inputs: Dict[str, pandas.DataFrame]
) -> "snowflake.snowpark.DataFrame":
    view_schema = fd.view_schema
    schema_dict = {col_name: view_schema.spark_type(col_name) for col_name in view_schema.column_names()}
    return pipeline_to_df_with_mock_input(
        session=session,
        pipeline=fd.pipeline,
        transformations=fd.transformations,
        output_schema=schema_dict,
        name=fd.name,
        fv_id=fd.id,
        mock_inputs=mock_inputs,
    )


def get_materialization_sql_str(
    feature_view: FeatureViewProto,
    # start is inclusive and end is exclusive
    time_limits: pendulum.Period,
    destination: str = None,
    storage_integration: Optional[str] = None,
) -> str:
    _load_template()
    source = feature_view.snowflake_data.snowflake_view_name
    if feature_view.HasField("temporal_aggregate"):
        source = MATERIALIZATION_TILE_TEMPLATE.render(
            source=source,
            join_keys=list(feature_view.join_keys),
            aggregations=_get_feature_view_aggregations(feature_view),
            slide_interval=feature_view.temporal_aggregate.slide_interval,
            timestamp_key=feature_view.timestamp_key,
        )
    return _format_sql(
        MATERIALIZATION_TEMPLATE.render(
            source=source,
            materialization_schema=feature_view.schemas.materialization_schema,
            timestamp_key=feature_view.timestamp_key,
            start_time=time_limits.start,
            end_time=time_limits.end,
            destination=destination,
            storage_integration=storage_integration,
        )
    )


def get_features_sql_str_for_spine(
    feature_set_config: FeatureSetConfig,
    timestamp_key: str,
    spine_sql: str = None,
    include_feature_view_timestamp_columns: bool = False,
) -> str:
    """
    Get a SQL string to fetch features given the spine and feature set.
    spine_sql and spine_table_name cannot be both empty.

    :param feature_set_config: FeatureSetConfig for the features.
    :param timestamp_key: Name of the time column in the spine.
    :param spine_sql: SQL str to get the spine.
    :param include_feature_view_timestamp_columns: (Optional) Include timestamp columns for every individual feature definitions.
    :return: A SQL string that can be used to fetch features.
    """
    _load_template()
    if include_feature_view_timestamp_columns:
        # TODO(TEC-7238): Implement this
        raise TectonSnowflakeNotImplementedError(
            "include_feature_view_timestamp_columns is not implemented for Snowflake"
        )

    feature_set_items = feature_set_config._get_feature_definitions_and_join_configs()
    input_items = []
    for item in feature_set_items:
        fd = item.feature_definition
        feature_view = fd.fv
        join_keys = {key: value for key, value in item.join_keys}
        features = [
            col_name
            for col_name in fd.view_schema.column_names()
            if col_name not in (list(join_keys.keys()) + [fd.timestamp_key])
        ]
        if len(fd.online_serving_index.join_keys) != len(fd.join_keys):
            raise ValueError("SQL string does not support wildcard")
        sql_str = TIME_LIMIT_TEMPLATE.render(
            source=pipeline_to_sql_string(
                pipeline=fd.pipeline,
                data_sources=fd.data_sources,
                transformations=fd.transformations,
            ),
            timestamp_key=fd.timestamp_key,
            # Apply time limit from feature_start_time
            start_time=fd.start_timestamp,
        )
        input_items.append(
            _FeatureSetItemInput(
                name=fd.name,
                timestamp_key=fd.timestamp_key,
                join_keys=join_keys,
                features=features,
                sql=sql_str,
                aggregation=(feature_view.temporal_aggregate if feature_view.HasField("temporal_aggregate") else None),
                ttl_seconds=(int(fd.serving_ttl.total_seconds()) if fd.is_temporal else None),
            )
        )
    return _format_sql(
        HISTORICAL_FEATURES_TEMPLATE.render(
            feature_set_items=input_items,
            spine_timestamp_key=timestamp_key,
            spine_sql=spine_sql,
            include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
        )
    )


def _get_feature_view_aggregations(feature_view: FeatureViewProto) -> Dict[str, Set[str]]:
    aggregations = defaultdict(set)
    for feature in feature_view.temporal_aggregate.features:
        aggregate_function = AGGREGATION_PLANS[feature.function]
        if not aggregate_function:
            raise TectonSnowflakeNotImplementedError(
                f"Unsupported aggregation function {feature.function} in snowflake pipeline"
            )
        aggregations[feature.input_feature_name].update(aggregate_function)

    # Need to order the functions for deterministic results.
    for key, value in aggregations.items():
        aggregations[key] = sorted(value)

    return aggregations
