from datetime import datetime
from typing import Dict
from typing import Optional
from typing import Union

import pandas
import pendulum

from tecton.interactive.data_frame import DataFrame
from tecton.interactive.run_api import validate_ondemand_mock_inputs_keys
from tecton.snowflake_context import SnowflakeContext
from tecton_proto.data.feature_view_pb2 import FeatureView as FeatureViewProto
from tecton_spark.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_spark.feature_set_config import FeatureSetConfig
from tecton_spark.snowflake import sql_helper
from tecton_spark.snowflake.errors import TectonSnowflakeNotImplementedError


def get_historical_features(
    feature_set_config: FeatureSetConfig,
    spine: Optional[Union["snowflake.snowpark.DataFrame", pandas.DataFrame, DataFrame, str]] = None,
    timestamp_key: Optional[str] = None,
    include_feature_view_timestamp_columns: bool = False,
    from_source: bool = False,
    save: bool = False,
    save_as: Optional[str] = None,
    start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
    end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
    entities: Optional[Union["snowflake.snowpark.DataFrame", pandas.DataFrame, DataFrame]] = None,
) -> DataFrame:
    if spine is None:
        raise TectonSnowflakeNotImplementedError("spine is required for Snowflake")

    if timestamp_key is None:
        raise TectonSnowflakeNotImplementedError("timestamp_key must be specified with Snowflake")

    # TODO(TEC-6991): Dataset doesn't really work with snowflake as it has spark dependency.
    # Need to rewrite it with snowflake context or remove this param for snowflake.
    if save or save_as is not None:
        raise TectonSnowflakeNotImplementedError("save is not supported for Snowflake")

    # TODO(TEC-6996): Implement this
    if entities is not None:
        raise TectonSnowflakeNotImplementedError("entities is not supported for Snowflake")

    # TODO(TEC-7010): Implement this
    if start_time is not None or end_time is not None:
        raise TectonSnowflakeNotImplementedError("start_time and end_time are not supported for Snowflake")

    df = DataFrame._create_with_snowflake(
        sql_helper.get_historical_features(
            spine=spine,
            session=SnowflakeContext.get_instance().get_session(),
            timestamp_key=timestamp_key,
            feature_set_config=feature_set_config,
            include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
        )
    )
    return df


def run_batch(
    fv_proto: FeatureViewProto,
    mock_inputs: Dict[str, Union[pandas.DataFrame, DataFrame]],
    feature_start_time: Union[pendulum.DateTime, datetime] = None,
    feature_end_time: Union[pendulum.DateTime, datetime] = None,
    aggregation_level: str = None,
) -> DataFrame:
    # TODO(TEC-7053): Implement this
    if len(mock_inputs) > 0:
        raise TectonSnowflakeNotImplementedError("mock_inputs is not supported for Snowflake")

    if fv_proto.HasField("temporal_aggregate"):
        for feature in fv_proto.temporal_aggregate.features:
            aggregate_function = sql_helper.AGGREGATION_PLANS[feature.function]
            if not aggregate_function:
                raise TectonSnowflakeNotImplementedError(
                    f"Unsupported aggregation function {feature.function} in snowflake pipeline"
                )

    return DataFrame._create_with_snowflake(
        sql_helper.run_batch(
            session=SnowflakeContext.get_instance().get_session(),
            feature_view=fv_proto,
            feature_start_time=feature_start_time,
            feature_end_time=feature_end_time,
            aggregation_level=aggregation_level,
        )
    )


def run_ondemand(
    fd: FeatureDefinition, mock_inputs: Dict[str, Union[pandas.DataFrame, DataFrame]]
) -> "tecton.interactive.data_frame.DataFrame":
    # Convert all inputs to pandas dataframes
    for key in mock_inputs:
        if isinstance(mock_inputs[key], DataFrame):
            mock_inputs[key] = mock_inputs[key].toPandas()

    # Validate that all the mock_inputs matchs with FV inputs, and that num rows match across all mock_inputs.
    validate_ondemand_mock_inputs_keys(mock_inputs, fd.feature_view_proto)

    # Execute Pandas pipeline to get output DataFrame.
    return DataFrame._create_with_snowflake(
        sql_helper.run_ondemand(
            session=SnowflakeContext.get_instance().get_session(),
            fd=fd,
            mock_inputs=mock_inputs,
        )
    )
