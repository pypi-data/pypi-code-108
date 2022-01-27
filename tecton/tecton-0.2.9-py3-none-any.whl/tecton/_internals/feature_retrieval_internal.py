from datetime import datetime
from typing import List
from typing import Mapping
from typing import Optional
from typing import Union

import pandas as pd
import pendulum
import pyspark
from pyspark.sql import functions

from tecton import conf
from tecton._internals import data_frame_helper
from tecton._internals import errors as internal_errors
from tecton._internals import metadata_service
from tecton._internals.feature_views import aggregations
from tecton._internals.utils import is_bfc_mode_single
from tecton._internals.utils import is_live_workspace
from tecton.interactive.data_frame import DataFrame
from tecton.interactive.feature_set_config import FeatureDefinitionAndJoinConfig
from tecton.tecton_context import TectonContext
from tecton.tecton_errors import TectonValidationError
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.data.feature_view_pb2 import FeatureView as FeatureViewProto
from tecton_proto.metadataservice.metadata_service_pb2 import GetFeatureViewRequest
from tecton_spark.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_spark.id_helper import IdHelper
from tecton_spark.materialization_params import MaterializationParams


def get_features(
    fd: FeatureDefinition,
    entities: Optional[Union[pyspark.sql.dataframe.DataFrame, pd.DataFrame, DataFrame]] = None,
    start_time: Optional[pendulum.DateTime] = None,
    end_time: Optional[pendulum.DateTime] = None,
    from_source: bool = False,
    is_read_api: bool = False,
) -> DataFrame:
    if fd.is_on_demand:
        raise internal_errors.FV_NOT_SUPPORTED_GET_HISTORICAL_FEATURES

    if from_source and fd.is_feature_table:
        raise TectonValidationError("FeatureTables are not compatible with from_source=True")

    if from_source and is_bfc_mode_single(fd):
        raise internal_errors.FV_BFC_SINGLE_FROM_SOURCE

    if not from_source and not is_live_workspace(fd.workspace):
        raise internal_errors.FD_GET_MATERIALIZED_FEATURES_FROM_DEVELOPMENT_WORKSPACE(fd.name, fd.workspace)

    if not from_source and not fd.writes_to_offline_store:
        raise internal_errors.FD_GET_FEATURES_MATERIALIZATION_DISABLED(fd.name)

    if start_time is not None and isinstance(start_time, datetime):
        start_time = pendulum.instance(start_time)
    if end_time is not None and isinstance(end_time, datetime):
        end_time = pendulum.instance(end_time)

    if fd.is_temporal_aggregate or fd.is_temporal:
        params = MaterializationParams.from_feature_definition(fd)
        assert params is not None, "Materialization params cannot be None"
        _start = start_time or params.from_timestamp
        _end = end_time or params.most_recent_anchor(pendulum.now("UTC"))
        time_range = pendulum.Period(_start, _end)
    else:
        _start = start_time or pendulum.datetime(1970, 1, 1)
        _end = end_time or pendulum.now("UTC")
        time_range = pendulum.Period(_start, _end)

    tc = TectonContext.get_instance()
    spark = tc._spark

    # Validate that entities only contains Join Key Columns.
    if entities is not None:
        if isinstance(entities, pd.DataFrame):
            entities = spark.createDataFrame(entities)
        if isinstance(entities, DataFrame):
            entities = entities.to_spark()
        assert set(entities.columns).issubset(
            set(fd.join_keys)
        ), f"Entities should only contain columns that can be used as Join Keys: {fd.join_keys}"

    try:
        if fd.is_temporal or fd.is_feature_table:
            df = aggregations.get_all_temporal_ft_features(spark, fd, entities, not from_source, time_range)
        else:
            df = data_frame_helper._get_feature_dataframe_with_limits(
                fd,
                spine=None,
                spine_time_limits=time_range,
                use_materialized_data=not from_source,
                spine_time_key=None,
                validate_time_key=False,
            ).to_spark()
            if entities is not None:
                df = df.join(functions.broadcast(entities.distinct()), entities.columns, how="right")
            columns = fd.join_keys + fd.features + [fd.timestamp_key]
            df = df.select(*columns)
    except pyspark.sql.utils.AnalysisException as e:
        if "Unable to infer schema for Parquet" in e.desc or "doesn't exist" in e.desc:
            if fd.is_feature_table:
                return DataFrame._create(tc._spark.createDataFrame([], fd.view_schema.to_spark()))
            else:
                raise internal_errors.FV_NO_MATERIALIZED_DATA(fd.name)
        raise
    # for FVs, raw data filtering should produce data already in the time range for adhoc
    # if FV output is outside feature time range given raw data, we do not want to filter it so the time validation
    # in materialization_plan._possibly_apply_feature_time_limits can fail the query. If we filter here, the UDF
    # may be executed after the filter step, when we want it to catch all features generated outside the time range
    # in ad hoc. It's not 100% but for this it may be good enough
    should_filter_by_time = not from_source
    if should_filter_by_time:
        if _start:
            df = df.filter(df[fd.timestamp_key] > _start)
        if _end:
            df = df.filter(df[fd.timestamp_key] < _end)

    return DataFrame._create(df)


def _get_feature_view_proto(fv_reference: str, workspace_name: Optional[str] = None) -> FeatureViewProto:
    # returns the proto for a feature view/table (a feature table is represented by a FeatureView proto)
    # we are NOT calling the get_feature_view() method because it will throw an error if you call it on a feature table
    request = GetFeatureViewRequest()
    request.version_specifier = fv_reference
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().GetFeatureView(request)
    if not response.HasField("feature_view"):
        raise internal_errors.FEATURE_DEFINITION_NOT_FOUND(fv_reference)
    return response.feature_view


def find_dependent_feature_set_items(
    node: PipelineNode, visited_inputs: Mapping[str, bool], fv_id: str, workspace_name: str
) -> List[FeatureDefinitionAndJoinConfig]:
    if node.HasField("feature_view_node"):
        if node.feature_view_node.input_name in visited_inputs:
            return []
        visited_inputs[node.feature_view_node.input_name] = True

        fv_proto = _get_feature_view_proto(
            IdHelper.to_string(node.feature_view_node.feature_view_id), workspace_name=workspace_name
        )
        fd = FeatureDefinition(fv_proto)

        join_keys = []
        overrides = {
            colpair.feature_column: colpair.spine_column
            for colpair in node.feature_view_node.feature_view.override_join_keys
        }
        for join_key in fv_proto.join_keys:
            potentially_overriden_key = overrides.get(join_key, join_key)
            join_keys.append((potentially_overriden_key, join_key))
        cfg = FeatureDefinitionAndJoinConfig(
            feature_definition=fd,
            name=fd.name,
            join_keys=join_keys,
            namespace=f"_udf_internal_{node.feature_view_node.input_name}_{fv_id}",
            features=node.feature_view_node.feature_view.features or fd.features,
        )

        return [cfg]
    elif node.HasField("transformation_node"):
        ret: List[FeatureDefinitionAndJoinConfig] = []
        for child in node.transformation_node.inputs:
            ret = ret + find_dependent_feature_set_items(child.node, visited_inputs, fv_id, workspace_name)
        return ret
    return []
