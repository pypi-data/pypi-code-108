import datetime
import functools
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pendulum
from typeguard import typechecked

from tecton.data_sources.data_source import BatchDataSource
from tecton.data_sources.data_source import StreamDataSource
from tecton.entities.entity import Entity
from tecton.entities.entity import OverriddenEntity
from tecton.feature_views.feature_view import _UnboundedInput
from tecton.feature_views.feature_view import Input
from tecton.feature_views.feature_view import MaterializedFeatureView
from tecton.features_common.feature_configs import DatabricksClusterConfig
from tecton.features_common.feature_configs import DeltaConfig
from tecton.features_common.feature_configs import DynamoConfig
from tecton.features_common.feature_configs import EMRClusterConfig
from tecton.features_common.feature_configs import ExistingClusterConfig
from tecton.features_common.feature_configs import FeatureAggregation
from tecton.features_common.feature_configs import MonitoringConfig
from tecton.features_common.feature_configs import ParquetConfig
from tecton.features_common.feature_configs import RedisConfig
from tecton.transformations.transformation import transformation
from tecton_proto.args.feature_view_pb2 import FeatureViewType
from tecton_proto.args.virtual_data_source_pb2 import DataSourceType

# This is the mode used when the feature view decorator is used on a pipeline function, i.e. one that only contains
# references to transformations and constants.
PIPELINE_MODE = "pipeline"


FRAMEWORK_VERSION_4 = 4


@typechecked
def stream_feature_view(
    *,
    mode: str,
    source: StreamDataSource,
    entities: List[Union[Entity, OverriddenEntity]],
    aggregation_slide_period: Optional[str] = None,  # TAFV ONLY
    aggregations: List[FeatureAggregation] = [],  # TAFV ONLY
    online: Optional[bool] = False,
    offline: Optional[bool] = False,
    ttl: Optional[str] = None,  # TFV ONLY
    feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]] = None,
    batch_schedule: Optional[str] = None,
    max_batch_aggregation_interval: Optional[str] = None,
    online_serving_index: Optional[List[str]] = None,
    batch_cluster_config: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    stream_cluster_config: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    offline_config: Optional[Union[ParquetConfig, DeltaConfig]] = ParquetConfig(),
    online_config: Optional[Union[DynamoConfig, RedisConfig]] = None,
    monitoring: Optional[MonitoringConfig] = None,
    description: str = "",
    owner: str = "",
    family: str = "",
    tags: Optional[Dict[str, str]] = None,
    timestamp_key: Optional[str] = None,
    name_override: Optional[str] = None,
):
    def decorator(user_function):
        if mode == PIPELINE_MODE:
            pipeline_function = user_function
            inferred_transform = None
        else:
            # Separate out the Transformation and manually construct a simple pipeline function.
            # We infer owner/family/tags but not a description.
            inferred_transform = transformation(mode, name_override, description, owner, family, tags)(user_function)

            def pipeline_function(**kwargs):
                return inferred_transform(**kwargs)

        inputs = {source.name: Input(source)}
        nonlocal aggregations
        if aggregations:
            assert aggregation_slide_period, "`aggregation_slide_period` is required if specifying aggregations"
            assert ttl is None, "`ttl` is automatically set for aggregations to the `aggregation_slide_period`"
            feature_view_type = FeatureViewType.FEATURE_VIEW_TYPE_TEMPORAL_AGGREGATE
        else:
            assert (
                aggregation_slide_period is None
            ), "`aggregation_slide_period` can only be specified when using `aggregations`"

            # Explicitly set aggregations to None (in case it is an empty list)
            aggregations = None

            feature_view_type = FeatureViewType.FEATURE_VIEW_TYPE_TEMPORAL

        featureView = MaterializedFeatureView(
            feature_view_type=feature_view_type,
            name=name_override or user_function.__name__,
            pipeline_function=pipeline_function,
            inferred_transform=inferred_transform,
            inputs=inputs,
            entities=entities,
            online=online,
            offline=offline,
            offline_config=offline_config,
            online_config=online_config,
            aggregation_slide_period=aggregation_slide_period,
            aggregations=aggregations,
            ttl=ttl,
            feature_start_time=feature_start_time,
            batch_schedule=batch_schedule,
            max_batch_aggregation_interval=max_batch_aggregation_interval,
            online_serving_index=online_serving_index,
            batch_cluster_config=batch_cluster_config,
            stream_cluster_config=stream_cluster_config,
            monitoring=monitoring,
            description=description,
            owner=owner,
            family=family,
            tags=tags,
            timestamp_key=timestamp_key,
            data_source_type=DataSourceType.STREAM_WITH_BATCH,
            user_function=user_function,
            framework_version=FRAMEWORK_VERSION_4,
            backfill_config=None,
        )
        functools.update_wrapper(featureView, user_function)

        return featureView

    return decorator


@typechecked
def batch_feature_view(
    *,
    mode: str,
    source: BatchDataSource,
    entities: List[Union[Entity, OverriddenEntity]],
    aggregation_slide_period: Optional[str] = None,  # TAFV ONLY
    aggregations: List[FeatureAggregation] = [],  # TAFV ONLY
    online: Optional[bool] = False,
    offline: Optional[bool] = False,
    ttl: Optional[str] = None,  # TFV ONLY
    feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]] = None,
    batch_schedule: Optional[str] = None,
    max_batch_aggregation_interval: Optional[str] = None,
    online_serving_index: Optional[List[str]] = None,
    batch_cluster_config: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    offline_config: Optional[Union[ParquetConfig, DeltaConfig]] = ParquetConfig(),
    online_config: Optional[Union[DynamoConfig, RedisConfig]] = None,
    monitoring: Optional[MonitoringConfig] = None,
    description: str = "",
    owner: str = "",
    family: str = "",
    tags: Optional[Dict[str, str]] = None,
    timestamp_key: Optional[str] = None,
    name_override: Optional[str] = None,
):
    def decorator(user_function):
        if mode == PIPELINE_MODE:
            pipeline_function = user_function
            inferred_transform = None
        else:
            # Separate out the Transformation and manually construct a simple pipeline function.
            # We infer owner/family/tags but not a description.
            inferred_transform = transformation(mode, name_override, description, owner, family, tags)(user_function)

            def pipeline_function(**kwargs):
                return inferred_transform(**kwargs)

        inputs = {source.name: Input(source)}
        nonlocal aggregations
        if aggregations:
            assert aggregation_slide_period, "`aggregation_slide_period` is required if specifying aggregations"
            assert ttl is None, "`ttl` is automatically set for aggregations to the `aggregation_slide_period`"
            feature_view_type = FeatureViewType.FEATURE_VIEW_TYPE_TEMPORAL_AGGREGATE
        else:
            assert (
                aggregation_slide_period is None
            ), "`aggregation_slide_period` can only be specified when using `aggregations`"

            # Explicitly set aggregations to None (in case it is an empty list)
            aggregations = None

            feature_view_type = FeatureViewType.FEATURE_VIEW_TYPE_TEMPORAL

        featureView = MaterializedFeatureView(
            feature_view_type=feature_view_type,
            name=name_override or user_function.__name__,
            pipeline_function=pipeline_function,
            inferred_transform=inferred_transform,
            inputs=inputs,
            entities=entities,
            online=online,
            offline=offline,
            offline_config=offline_config,
            online_config=online_config,
            aggregation_slide_period=aggregation_slide_period,
            aggregations=aggregations,
            ttl=ttl,
            feature_start_time=feature_start_time,
            batch_schedule=batch_schedule,
            max_batch_aggregation_interval=max_batch_aggregation_interval,
            online_serving_index=online_serving_index,
            batch_cluster_config=batch_cluster_config,
            stream_cluster_config=None,
            monitoring=monitoring,
            description=description,
            owner=owner,
            family=family,
            tags=tags,
            timestamp_key=timestamp_key,
            data_source_type=DataSourceType.BATCH,
            user_function=user_function,
            framework_version=FRAMEWORK_VERSION_4,
            backfill_config=None,
        )
        functools.update_wrapper(featureView, user_function)

        return featureView

    return decorator


@typechecked
def custom_batch_feature_view(
    *,
    mode: str,
    sources: List[BatchDataSource],
    entities: List[Union[Entity, OverriddenEntity]],
    online: Optional[bool] = False,
    offline: Optional[bool] = False,
    ttl: Optional[str] = None,
    feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]] = None,
    batch_schedule: Optional[str] = None,
    batch_cluster_config: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    offline_config: Optional[Union[ParquetConfig, DeltaConfig]] = ParquetConfig(),
    online_config: Optional[Union[DynamoConfig, RedisConfig]] = None,
    monitoring: Optional[MonitoringConfig] = None,
    description: str = "",
    owner: str = "",
    family: str = "",
    tags: Optional[Dict[str, str]] = None,
    timestamp_key: Optional[str] = None,
    name_override: Optional[str] = None,
):
    def decorator(user_function):
        if mode == PIPELINE_MODE:
            pipeline_function = user_function
            inferred_transform = None
        else:
            # Separate out the Transformation and manually construct a simple pipeline function.
            # We infer owner/family/tags but not a description.
            inferred_transform = transformation(mode, name_override, description, owner, family, tags)(user_function)

            def pipeline_function(**kwargs):
                return inferred_transform(**kwargs)

        inputs = {ds.name: _UnboundedInput(ds) for ds in sources}

        featureView = MaterializedFeatureView(
            feature_view_type=FeatureViewType.FEATURE_VIEW_TYPE_TEMPORAL,
            name=name_override or user_function.__name__,
            pipeline_function=pipeline_function,
            inferred_transform=inferred_transform,
            inputs=inputs,
            entities=entities,
            online=online,
            offline=offline,
            offline_config=offline_config,
            online_config=online_config,
            aggregation_slide_period=None,
            aggregations=None,
            ttl=ttl,
            feature_start_time=feature_start_time,
            batch_schedule=batch_schedule,
            max_batch_aggregation_interval=None,
            online_serving_index=None,
            batch_cluster_config=batch_cluster_config,
            stream_cluster_config=None,
            monitoring=monitoring,
            description=description,
            owner=owner,
            family=family,
            tags=tags,
            timestamp_key=timestamp_key,
            data_source_type=DataSourceType.BATCH,
            user_function=user_function,
            framework_version=FRAMEWORK_VERSION_4,
            is_custom=True,
            backfill_config=None,
        )
        functools.update_wrapper(featureView, user_function)

        return featureView

    return decorator
