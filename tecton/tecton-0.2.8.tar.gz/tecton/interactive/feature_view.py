from datetime import datetime
from typing import *

import numpy as np
import pandas
import pendulum
import pyspark
from pyspark.sql import DataFrame
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.utils import AnalysisException

import tecton
from tecton import conf
from tecton._internals import data_frame_helper
from tecton._internals import errors
from tecton._internals import feature_retrieval_internal
from tecton._internals import metadata_service
from tecton._internals import utils
from tecton._internals.errors import FV_INVALID_MOCK_INPUTS
from tecton._internals.feature_views import aggregations
from tecton._internals.sdk_decorators import sdk_public_method
from tecton.feature_services.query_helper import _QueryHelper
from tecton.interactive.data_frame import DataFrame as TectonDataFrame
from tecton.interactive.data_frame import FeatureVector
from tecton.interactive.dataset import Dataset
from tecton.interactive.feature_definition import FeatureDefinition
from tecton.interactive.run_api import run_batch
from tecton.interactive.run_api import run_ondemand
from tecton.interactive.run_api import run_stream
from tecton.tecton_context import TectonContext
from tecton_proto.args.virtual_data_source_pb2 import DataSourceType
from tecton_proto.data import feature_view_pb2
from tecton_proto.metadataservice.metadata_service_pb2 import GetFeatureViewRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetServingStatusRequest
from tecton_spark import pipeline_helper
from tecton_spark.feature_definition_wrapper import FeatureDefinitionWrapper
from tecton_spark.logger import get_logger
from tecton_spark.materialization_params import MaterializationParams
from tecton_spark.pipeline_helper import find_request_context
from tecton_spark.pipeline_helper import pipeline_to_dataframe
from tecton_spark.pipeline_helper import run_mock_pandas_pipeline
from tecton_spark.transformation import _RequestContext

logger = get_logger("FeatureView")


__all__ = ["FeatureView", "get_feature_view"]


class FeatureView(FeatureDefinition):
    """
    FeatureView class.

    To get a FeatureView instance, call :py:func:`tecton.get_feature_view`.
    """

    _proto: feature_view_pb2.FeatureView

    def __init__(self, proto):
        self._proto = proto

    @classmethod
    def _fco_type_name_singular_snake_case(cls) -> str:
        return "feature_view"

    @classmethod
    def _fco_type_name_plural_snake_case(cls) -> str:
        return "feature_views"

    def __str__(self):
        return f"FeatureView|{self.id}"

    def __repr__(self):
        return f"FeatureView(name='{self.name}')"

    @sdk_public_method
    def run(self, **mock_inputs: Union[pandas.DataFrame, DataFrame]):
        """
        Runs the feature view against passed-in mock data rather than the actual data sources.

        :param mock_inputs: kwargs with the same expected keys as the FeatureView's inputs parameter. Each input name maps to a Pandas DataFrame that should be evaluated for that node in the pipeline.
        """
        input_names = pipeline_helper.get_all_input_keys(self._proto.pipeline.root)
        if input_names != mock_inputs.keys():
            raise FV_INVALID_MOCK_INPUTS(mock_inputs.keys(), input_names)

        if type(self) == OnDemandFeatureView:
            return run_mock_pandas_pipeline(
                self._proto.pipeline, self._proto.enrichments.transformations, self.name, mock_inputs
            )
        else:
            tc = TectonContext.get_instance()
            spark = tc._spark
            return pipeline_to_dataframe(
                spark,
                pipeline=self._proto.pipeline,
                consume_streaming_data_sources=False,
                data_sources=[],
                transformations=self._proto.enrichments.transformations,
                feature_time_limits=None,
                schedule_interval=pendulum.Duration(
                    seconds=self._proto.materialization_params.schedule_interval.ToSeconds()
                ),
                mock_inputs=mock_inputs,
            )

    def _get_serving_status(self):
        request = GetServingStatusRequest()
        request.feature_package_id.CopyFrom(self._proto.feature_view_id)
        request.workspace = self.workspace
        return metadata_service.instance().GetServingStatus(request)

    @sdk_public_method
    def preview(self, limit=10, time_range: Optional[pendulum.Period] = None, use_materialized_data: bool = True):
        """
        Deprecated.
        Shows a preview of the FeatureView's features. Random, unique join_keys are chosen to showcase the features.

        :param limit: (Optional, default=10) The number of rows to preview
        :param time_range: (Optional) Time range to collect features from. Will default to recent data (past 2 days).
        :param use_materialized_data: (Optional) Use materialized data if materialization is enabled.
        :return: A Tecton :class:`DataFrame`.
        """
        logger.warning(
            "Deprecated. Use the 'get_historical_features' method instead to view historical values for this feature view. "
            + "See api reference for this feature view type. Example: https://docs.tecton.ai/api-reference/stubs/tecton.interactive.BatchWindowAggregateFeatureView.html#tecton.interactive.BatchWindowAggregateFeatureView.get_historical_features"
        )
        if self.type == "OnDemand":
            raise errors.FV_NOT_SUPPORTED_GET_FEATURE_DF

        try:
            pandas_df = (
                data_frame_helper._get_feature_dataframe_with_limits(
                    FeatureDefinitionWrapper(self._proto),
                    spine=None,
                    spine_time_key=None,
                    spine_time_limits=time_range,
                    use_materialized_data=use_materialized_data,
                )
                .to_spark()
                .drop_duplicates(self.join_keys)
                .limit(limit)
                .toPandas()
            )
        except AnalysisException as e:
            if "Path does not exist:" in e.desc:
                raise errors.FD_PREVIEW_NO_MATERIALIZED_OFFLINE_DATA
            else:
                raise e

        if len(pandas_df) == 0:
            # spine_time_limits refers to the range of feature timestamps. Converting to the corresponding raw data time range.
            raw_data_time_limits = aggregations._get_time_limits(
                fd=FeatureDefinitionWrapper(self._proto), spine_df=None, spine_time_limits=time_range
            )
            time_range_type = "default" if time_range is None else "provided"
            logger.warn(
                f"No preview data could be generated because no data was found in the {time_range_type} "
                f"time range of {raw_data_time_limits}. To specify a different time range, set the parameter 'time_range'"
            )
        return tecton.interactive.data_frame.set_pandas_timezone_from_spark(pandas_df)

    def _assert_writes_to_offline_feature_store(self):
        if not self._writes_to_offline_feature_store:
            raise errors.FV_NEEDS_TO_BE_MATERIALIZED(self.name)

    @sdk_public_method
    def get_feature_dataframe(
        self,
        spine: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, None] = None,
        spine_time_key: str = None,
        use_materialized_data: bool = True,
        save: bool = None,
        save_as: str = None,
    ) -> "tecton.interactive.data_frame.DataFrame":
        """
        Deprecated.
        Returns a Tecton :class:`DataFrame` that contains the output Feature Transformation of the Feature View.

        :param spine: (Optional) The spine to join against, as a dataframe.
            If present, the returned data frame will contain rollups for all (join key, temporal key)
            combinations that are required to compute a full frame from the spine. If spine is not
            specified, it'll return a dataframe with sample feature vectors.
        :param spine_time_key: (Optional) Name of the time column in spine.
            If unspecified, will default to the time column of the spine if there is only one present.
        :param use_materialized_data: (Optional) Use materialized data if materialization is enabled
        :param save: (Optional) set to True to persist DataFrame as a Dataset object
        :param save_as: (Optional) name to save the DataFrame as. Not applicable when save=False.
            If unspecified and save=True, a name will be generated.
        :return: A Tecton :class:`DataFrame`.
        """
        logger.warning(
            "Deprecated. Use the 'get_historical_features' method instead to view historical values for this feature view. "
            + "See api reference for this feature view type. Example: https://docs.tecton.ai/api-reference/stubs/tecton.interactive.BatchWindowAggregateFeatureView.html#tecton.interactive.BatchWindowAggregateFeatureView.get_historical_features"
        )
        from tecton.tecton_context import TectonContext

        tc = TectonContext.get_instance()
        # TODO: be able to use self._get_feature_dataframe_with_limits directly
        # doing it this way for now to return timestamps provided by user rather than anchor times

        if self.type == "OnDemand" and spine is None:
            raise errors.FV_GET_FEATURE_DF_NO_SPINE

        # same checks as in _get_historical_features but using correct param names for get_feature_dataframe
        is_live_workspace = utils.is_live_workspace(self.workspace)
        if use_materialized_data and not is_live_workspace and not self.type == "OnDemand":
            raise errors.FD_GET_MATERIALIZED_FEATURES_FROM_DEVELOPMENT_WORKSPACE_GFD(self.name, self.workspace)

        if use_materialized_data and not self.type == "OnDemand" and not self._proto.materialization_enabled:
            raise errors.FD_GET_FEATURES_MATERIALIZATION_DISABLED_GFD(self.name)

        TectonContext.validate_spine_type(spine)
        timestamp_key = spine_time_key
        if self._should_infer_timestamp_of_spine(timestamp_key, spine):
            timestamp_key = utils.infer_timestamp(spine)

        feature_set_config = self._construct_feature_set_config()
        if any(fv.is_feature_table for fv in feature_set_config.feature_definitions):
            if not is_live_workspace:
                raise errors.FV_WITH_FT_DEVELOPMENT_WORKSPACE
            elif not use_materialized_data:
                raise errors.USE_MATERIALIZED_DATA_WITH_FT

        df = tc.execute(
            spine,
            feature_set_config=feature_set_config,
            timestamp_key=timestamp_key,
            use_materialized_data=use_materialized_data,
        )
        if save or save_as is not None:
            return Dataset._create(
                df=df,
                save_as=save_as,
                workspace=self.workspace,
                feature_definition_id=self.id,
                spine=spine,
                timestamp_key=timestamp_key,
            )
        return df

    @sdk_public_method
    def get_historical_features(
        self,
        spine: Optional[Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, TectonDataFrame]] = None,
        timestamp_key: Optional[str] = None,
        start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        entities: Optional[Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, TectonDataFrame]] = None,
        from_source: bool = False,
        save: bool = False,
        save_as: Optional[str] = None,
    ) -> TectonDataFrame:
        """
        Returns a Tecton :class:`DataFrame` of historical values for this feature view.
        If no arguments are passed in, all feature values for this feature view will be returned in a Tecton DataFrame.

        Note:
        The `timestamp_key` parameter is only applicable when a spine is passed in.
        Parameters `start_time`, `end_time`, and `entities` are only applicable when a spine is not passed in.

        :param spine: (Optional) The spine to join against, as a dataframe.
            If present, the returned DataFrame will contain rollups for all (join key, temporal key)
            combinations that are required to compute a full frame from the spine.
            To distinguish between spine columns and feature columns, feature columns are labeled as
            `feature_view_name.feature_name` in the returned DataFrame.
            If spine is not specified, it'll return a DataFrame of feature values in the specified time range.
        :type spine: Union[pyspark.sql.DataFrame, pandas.DataFrame, tecton.DataFrame]
        :param timestamp_key: (Optional) Name of the time column in the spine.
            This method will fetch the latest features computed before the specified timestamps in this column.
            If unspecified, will default to the time column of the spine if there is only one present.
            If more than one time column is present in the spine, you must specify which column you'd like to use.
        :type timestamp_key: str
        :param start_time: (Optional) The interval start time from when we want to retrieve features.
            If no timezone is specified, will default to using UTC.
        :type start_time: Union[pendulum.DateTime, datetime.datetime]
        :param end_time: (Optional) The interval end time until when we want to retrieve features.
            If no timezone is specified, will default to using UTC.
        :type end_time: Union[pendulum.DateTime, datetime.datetime]
        :param entities: (Optional) Filter feature data returned to a set of entity IDs.
            If specified, this DataFrame should only contain join key columns.
        :type entities: Union[pyspark.sql.DataFrame, pandas.DataFrame, tecton.DataFrame]
        :param from_source: (Optional) Whether feature values should be recomputed from the original data source.
            If False, we will read the materialized values from the offline store.
        :type from_source: bool
        :param save: (Optional) Whether to persist the DataFrame as a Dataset object. Default is False.
        :type save: bool
        :param save_as: (Optional) Name to save the DataFrame as.
            If unspecified and save=True, a name will be generated.
        :type save_as: str

        Examples:
            A FeatureView :py:mod:`fv` with join key :py:mod:`user_id`.

            1) :py:mod:`fv.get_historical_features(spine)` where :py:mod:`spine=pandas.Dataframe({'user_id': [1,2,3],
            'date': [datetime(...), datetime(...), datetime(...)]})`
            Fetch historical features from the offline store for users 1, 2, and 3 for the specified timestamps in the spine.

            2) :py:mod:`fv.get_historical_features(spine, save_as='my_dataset)` where :py:mod:`spine=pandas.Dataframe({'user_id': [1,2,3], 'date': [datetime(...), datetime(...), datetime(...)]})`
            Fetch historical features from the offline store for users 1, 2, and 3 for the specified timestamps in the spine. Save the DataFrame as dataset with the name :py:mod`my_dataset`.

            3) :py:mod:`fv.get_historical_features(spine, timestamp_key='date_1')` where :py:mod:`spine=pandas.Dataframe({'user_id': [1,2,3], 'date_1': [datetime(...), datetime(...), datetime(...)], 'date_2': [datetime(...), datetime(...), datetime(...)]})`
            Fetch historical features from the offline store for users 1, 2, and 3 for the specified timestamps in the 'date_1' column in the spine.

            4) :py:mod:`fv.get_historical_features(start_time=datetime(...), end_time=datetime(...))`
            Fetch all historical features from the offline store in the time range specified by `start_time` and `end_time`.

        :return: A Tecton :class:`DataFrame`.
        """
        return self._get_historical_features(
            spine, timestamp_key, start_time, end_time, entities, from_source, save, save_as
        )

    def _upload_df_spark(self, df_path: str, df: pyspark.sql.dataframe.DataFrame):
        df.write.parquet(df_path)

    @property
    def timestamp_key(self) -> Optional[str]:
        """
        Returns the timestamp_key column name of this FeatureView.
        """
        if self._proto.HasField("timestamp_key"):
            return self._proto.timestamp_key
        return None

    # TODO:(samantha) delete this property
    @property
    def is_temporal_aggregate(self):
        """
        Deprecated. Please use the type property for this feature view.
        Returns whether or not this FeatureView is of type TemporalAggregateFeatureView.
        """
        logger.warning(
            "Deprecated. Please use the type property of this feature view or the built-in python type() method."
        )
        return self._proto.HasField("temporal_aggregate")

    # TODO:(samantha) delete this property
    @property
    def is_temporal(self):
        """
        Deprecated. Please use the type property for this feature view.
        Returns whether or not this FeatureView is of type TemporalFeatureView.
        """
        logger.warning(
            "Deprecated. Please use the type property of this feature view or the built-in python type() method."
        )
        return self._proto.HasField("temporal")

    # TODO:(samantha) delete this property
    @property
    def is_on_demand(self):
        """
        Deprecated. Please use the type property for this feature view.
        Returns whether or not this FeatureView is of type OnDemandFeatureView.
        """
        logger.warning(
            "Deprecated. Please use the type property of this feature view or the built-in python type() method."
        )
        return self._proto.HasField("on_demand_feature_view")

    @property
    def _writes_to_offline_feature_store(self) -> bool:
        """
        Returns if the FeatureView materialization is enabled to write to the OfflineStore.
        Return value does not reflect the completion of any specific materialization job.
        """
        return self._proto.materialization_enabled and self._proto.materialization_params.writes_to_offline_store

    @property
    def _writes_to_online_feature_store(self) -> bool:
        """
        Returns if the FeatureView materialization is enabled to write to the OnlineStore.
        Return value does not reflect the completion of any specific materialization job.
        """
        return self._proto.materialization_enabled and self._proto.materialization_params.writes_to_online_store

    @property
    def _materialization_params(self) -> Optional[MaterializationParams]:
        return MaterializationParams.from_proto(self._proto)

    @property  # type: ignore
    @sdk_public_method
    def feature_start_time(self) -> Optional[pendulum.DateTime]:
        """
        This represents the time at which features are first available.
        """
        if not self._proto.HasField("materialization_params"):
            return None
        return pendulum.from_timestamp(self._proto.materialization_params.start_timestamp.ToSeconds())

    def _batch_materialization_schedule(self) -> Optional[pendulum.Duration]:
        if not self._proto.HasField("materialization_params"):
            return None
        # TODO: this should return a formatted duration, not a timestamp
        return pendulum.Duration(seconds=self._proto.materialization_params.schedule_interval.ToSeconds())

    def _schedule_offset(self) -> Optional[pendulum.Duration]:
        if not self._proto.HasField("materialization_params"):
            return None
        schedule_offset = pendulum.duration(
            seconds=self._proto.materialization_params.allowed_upstream_lateness.ToSeconds()
        )
        if not schedule_offset:
            return None
        return schedule_offset

    @sdk_public_method
    def get_features(
        self,
        entities: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, None] = None,
        start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        from_source: bool = False,
    ) -> "tecton.interactive.data_frame.DataFrame":
        """
        Deprecated.
        Returns all the feature values that are defined by this Feature View in the specified time range.

        :param entities: (Optional) Filter feature data to a set of entity IDs.
            If specified, this DataFrame should only contain join key columns.
        :param start_time: (Optional) The interval start time from when we want to retrieve features.
        :param end_time:  (Optional) The interval end time until when we want to retrieve features.
        :param from_source: Whether feature values should be recomputed from the original data source.
            If False, we will attempt to read the values from the materialized store.

        :return: A Tecton DataFrame with features values.
        """
        logger.warning(
            "Deprecated. Use the 'get_historical_features' method instead to view historical values for this feature view. "
            + "See api reference for this feature view type. Example: https://docs.tecton.ai/api-reference/stubs/tecton.interactive.BatchWindowAggregateFeatureView.html#tecton.interactive.BatchWindowAggregateFeatureView.get_historical_features"
        )

        fd = FeatureDefinitionWrapper(self._proto)
        return feature_retrieval_internal.get_features(fd, entities, start_time, end_time, from_source)

    @sdk_public_method
    def get_feature_vector(
        self,
        join_keys: Optional[Mapping[str, Union[int, np.int_, str, bytes]]] = None,
        include_join_keys_in_response: bool = False,
        request_context_map: Optional[Mapping[str, Union[int, np.int_, str, bytes, float]]] = None,
    ) -> FeatureVector:
        """
        Deprecated.
        Returns a single Tecton :class:`FeatureVector` from the Online Store.
        At least one of join_keys or request_context_map is required.

        :param join_keys: Join keys of the enclosed FeatureViews.
        :param include_join_keys_in_response: Whether to include join keys as part of the response FeatureVector.
        :param request_context_map: Dictionary of request context values.

        :return: A :class:`FeatureVector` of the results.
        """
        logger.warning(
            "Deprecated. Use the 'get_online_features' method instead to fetch features from the Online Store for this feature view. "
            + "See the api reference for this feature view type. Example: https://docs.tecton.ai/api-reference/stubs/tecton.interactive.BatchWindowAggregateFeatureView.html#tecton.interactive.BatchWindowAggregateFeatureView.get_online_features"
        )
        # doing checks here instead of get_online_features in order to provide the correct error messages
        if not self._writes_to_online_feature_store and not self.type == "OnDemand":
            raise errors.UNSUPPORTED_OPERATION(
                "get_feature_vector", "online_serving_enabled is not set to True for this FeatureView."
            )
        if join_keys is None and request_context_map is None:
            raise errors.FS_GET_FEATURE_VECTOR_REQUIRED_ARGS
        if self.type == "OnDemand":
            # validate request_context_map
            required_request_context_keys = list(self._request_context.arg_to_schema.keys())
            if len(required_request_context_keys) > 0 and request_context_map is None:
                raise errors.GET_FEATURE_VECTOR_FV_NO_REQUEST_DATA(required_request_context_keys)
            utils.validate_request_data(request_context_map, required_request_context_keys, is_read_api_v3=False)
            # check if we need join keys
            if join_keys is None and utils.get_num_dependent_fv(self._proto.pipeline.root, visited_inputs={}) > 0:
                raise errors.GET_ONLINE_FEATURES_ODFV_JOIN_KEYS
            return self.get_online_features(join_keys, include_join_keys_in_response, request_context_map)
        return self.get_online_features(join_keys, include_join_keys_in_response)

    @sdk_public_method
    def get_online_features(
        self,
        join_keys: Mapping[str, Union[int, np.int_, str, bytes]],
        include_join_keys_in_response: bool = False,
    ) -> FeatureVector:
        """
        Returns a single Tecton :class:`FeatureVector` from the Online Store.

        :param join_keys: Join keys of the enclosed FeatureViews.
        :param include_join_keys_in_response: Whether to include join keys as part of the response FeatureVector.

        Examples:
            A FeatureView :py:mod:`fv` with join key :py:mod:`user_id`.

            1) :py:mod:`fv.get_online_features(join_keys={'user_id': 1})`
            Fetch the latest features from the online store for user 1.

            2) :py:mod:`fv.get_online_features(join_keys={'user_id': 1}, include_join_keys_in_respone=True)`
            Fetch the latest features from the online store for user 1 and include the join key information (user_id=1) in the returned FeatureVector.

        :return: A :class:`FeatureVector` of the results.
        """
        if not self._writes_to_online_feature_store:
            raise errors.UNSUPPORTED_OPERATION(
                "get_online_features", "online_serving_enabled is not set to True for this FeatureView."
            )
        utils.validate_join_key_types(join_keys)

        return _QueryHelper(self._proto.fco_metadata.workspace, feature_view_name=self.name).get_feature_vector(
            join_keys or {},
            include_join_keys_in_response,
            {},
            self._request_context,
        )

    @property
    def _request_context(self) -> _RequestContext:
        return _RequestContext({})

    @property
    def _materialization_schema(self):
        from tecton_spark.schema import Schema

        return Schema(self._proto.schemas.materialization_schema)


def is_documented_by(original):
    def wrapper(target):
        target.__doc__ = original.__doc__
        return target

    return wrapper


class BatchWindowAggregateFeatureView(FeatureView):
    """
    BatchWindowAggregateFeatureView class.

    To get a FeatureView instance, call :py:func:`tecton.get_feature_view`.
    """

    @property  # type: ignore
    @sdk_public_method
    def batch_materialization_schedule(self) -> Optional[pendulum.Duration]:
        """
        This represents how often we schedule batch materialization jobs.
        """
        return self._batch_materialization_schedule()

    @property  # type: ignore
    @sdk_public_method
    def schedule_offset(self) -> Optional[pendulum.Duration]:
        """
        If this attribute is non-empty, Tecton will schedule materialization jobs at an offset equal to this.
        """
        return self._schedule_offset()

    @sdk_public_method
    def materialization_status(self, verbose=False, limit=1000, sort_columns=None, errors_only=False):
        """
        Displays materialization information for the FeatureView, which may include past jobs, scheduled jobs,
        and job failures. This method returns different information depending on the type of FeatureView.

        :param verbose: If set to true, method will display additional low level materialization information,
            useful for debugging.
        :param limit: Maximum number of jobs to return.
        :param sort_columns: A comma-separated list of column names by which to sort the rows.
        :param: errors_only: If set to true, method will only return jobs that failed with an error.
        """
        return self._materialization_status(verbose, limit, sort_columns, errors_only)

    @property  # type: ignore
    @sdk_public_method
    def type(self) -> str:
        """
        Returns the FeatureView type: 'TemporalAggregate'.
        """
        return "TemporalAggregate"

    @property  # type: ignore
    @sdk_public_method
    @is_documented_by(FeatureDefinition.features)
    def features(self) -> List[str]:
        return [f.output_feature_name for f in self._proto.temporal_aggregate.features]

    @sdk_public_method
    def run(
        self,
        feature_start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        feature_end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        aggregate_tiles: bool = None,
        aggregation_level: str = None,  # TODO(raviphol): Set this to "full" once aggregate_tiles is removed.
        **mock_inputs: Union[pandas.DataFrame, DataFrame],
    ) -> "tecton.interactive.data_frame.DataFrame":
        """
        Run the FeatureView on the fly. It supports mock input data, but if mock_inputs is not provided for some
        features, those inputs will be retrieved from the linked DataSources. In that case, the run may takes several
        minutes to retrieve the data.

        :param feature_start_time: Start time for the feature. mock_inputs and linked DataSources will be filtered in
            respect to providing neccessity inputs for this feature time.
            The output values with timestamps earlier than this will be dropped.
            If unset, default to feature_end_time minus materialization schedule interval.

        :param feature_end_time: End time for input data (both data sources, and mock_inputs). mock_inputs and linked
            DataSources will be filtered in respect to providing neccessity inputs for this feature time.
            The output values with timestamps later than this will be dropped.
            If unset, default to datetime now, at the time of a run.

        :param aggregate_tiles: [Deprecated - Please use aggregation_level="tile" instead]

        :param aggregation_level: This only works with aggregate FeatureView types. Select the level of aggregation
            over the output result dataframe. Avalable values are:

            1) :py:mod:`"full"` - Fully aggregate the features. The output rows for each of the time_windows specified in FeatureAggregation(s) under the FeatureView config will be aggregated together.

            2) :py:mod:`"partial"` - Aggregate the output rows under the same fixed-size sliding aggregate window. The size of the aggregate window is specified as aggregation_slide_period in the FeatureView config.

            3) :py:mod:`"disabled"` - No aggregation operation performed.

        :param \*\*mock_inputs: If provided, mock_inputs will be used as the FeatureView inputs for the Run, instead of
            the data from linked DataSources. The name of the parameter(s) must be a valid FeatureView input names.

        Examples:
            A FeatureView 'fv' with inputs: 'ds1', 'ds2'.

            1) :py:mod:`fv.run()` Use inputs from the linked DataSources for both ds1 and ds2. feature_end_time defaults 'now', and feature_start_time is set to feature_end_time - batch_schedule.

            2) :py:mod:`fv.run(feature_start_time=datetime(2021, 6, 21), feature_end_time=datetime(2021, 6, 22))` feature_start_time and feature_end_time set by users.

            3) :py:mod:`fv.run(ds1=mock_dataframe1)` Use mock_dataframe1 as input ds1, ds2 from a linked DataSource.

            4) :py:mod:`fv.run(ds1=mock_dataframe1, ds2=mock_dataframe2)` Use the mock dataframes for both ds1 and ds2.

        :return: A tecton DataFrame of the results.
        """
        return run_batch(
            self._proto, feature_start_time, feature_end_time, mock_inputs, aggregate_tiles, aggregation_level
        )


class BatchFeatureView(FeatureView):
    """
    BatchFeatureView class.

    To get a FeatureView instance, call :py:func:`tecton.get_feature_view`.
    """

    @property  # type: ignore
    @sdk_public_method
    @is_documented_by(BatchWindowAggregateFeatureView.batch_materialization_schedule)
    def batch_materialization_schedule(self) -> Optional[pendulum.Duration]:
        return self._batch_materialization_schedule()

    @property  # type: ignore
    @sdk_public_method
    @is_documented_by(BatchWindowAggregateFeatureView.schedule_offset)
    def schedule_offset(self) -> Optional[pendulum.Duration]:
        return self._schedule_offset()

    @sdk_public_method
    @is_documented_by(BatchWindowAggregateFeatureView.materialization_status)
    def materialization_status(self, verbose=False, limit=1000, sort_columns=None, errors_only=False):
        return self._materialization_status(verbose, limit, sort_columns, errors_only)

    @property  # type: ignore
    @sdk_public_method
    def type(self) -> str:
        """
        Returns the FeatureView type: 'Temporal'.
        """
        return "Temporal"

    @sdk_public_method
    def run(
        self,
        feature_start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        feature_end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        **mock_inputs: Union[pandas.DataFrame, DataFrame],
    ) -> "tecton.interactive.data_frame.DataFrame":
        """
        Run the FeatureView on the fly. It supports mock input data, but if mock_inputs is not provided for some
        features, those inputs will be retrieved from the linked DataSources. In that case, the run may takes several
        minutes to retrieve the data.

        :param feature_start_time: Start time for the feature. mock_inputs and linked DataSources will be filtered in
            respect to providing neccessity inputs for this feature time.
            The output values with timestamps earlier than this will be dropped.
            If unset, default to feature_end_time minus materialization schedule interval.

        :param feature_end_time: End time for input data (both data sources, and mock_inputs). mock_inputs and linked
            DataSources will be filtered in respect to providing neccessity inputs for this feature time.
            The output values with timestamps later than this will be dropped.
            If unset, default to datetime now, at the time of a run.

        :param \*\*mock_inputs: If provided, mock_inputs will be used as the FeatureView inputs for the Run, instead of
            the data from linked DataSources. The name of the parameter(s) must be a valid FeatureView input names.

        Examples:
            A FeatureView 'fv' with inputs: 'ds1', 'ds2'.

            1) :py:mod:`fv.run()` Use inputs from the linked DataSources for both ds1 and ds2. feature_end_time defaults 'now', and feature_start_time is set to feature_end_time - batch_schedule.

            2) :py:mod:`fv.run(feature_start_time=datetime(2021, 6, 21), feature_end_time=datetime(2021, 6, 22))` feature_start_time and feature_end_time set by users.

            3) :py:mod:`fv.run(ds1=mock_dataframe1)` Use mock_dataframe1 as input ds1, ds2 from a linked DataSource.

            4) :py:mod:`fv.run(ds1=mock_dataframe1, ds2=mock_dataframe2)` Use the mock dataframes for both ds1 and ds2.

        :return: A tecton DataFrame of the results.
        """
        return run_batch(self._proto, feature_start_time, feature_end_time, mock_inputs)


class StreamFeatureView(FeatureView):
    """
    StreamFeatureView class.

    To get a FeatureView instance, call :py:func:`tecton.get_feature_view`.
    """

    @property  # type: ignore
    @sdk_public_method
    @is_documented_by(BatchWindowAggregateFeatureView.batch_materialization_schedule)
    def batch_materialization_schedule(self) -> Optional[pendulum.Duration]:
        return self._batch_materialization_schedule()

    @property  # type: ignore
    @sdk_public_method
    @is_documented_by(BatchWindowAggregateFeatureView.schedule_offset)
    def schedule_offset(self) -> Optional[pendulum.Duration]:
        return self._schedule_offset()

    @sdk_public_method
    @is_documented_by(BatchWindowAggregateFeatureView.materialization_status)
    def materialization_status(self, verbose=False, limit=1000, sort_columns=None, errors_only=False):
        return self._materialization_status(verbose, limit, sort_columns, errors_only)

    @property  # type: ignore
    @sdk_public_method
    @is_documented_by(BatchFeatureView.type)
    def type(self) -> str:
        return "Temporal"

    @sdk_public_method
    @is_documented_by(BatchFeatureView.run)
    def run(
        self,
        feature_start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        feature_end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        **mock_inputs: Union[pandas.DataFrame, DataFrame],
    ) -> "tecton.interactive.data_frame.DataFrame":
        return run_batch(self._proto, feature_start_time, feature_end_time, mock_inputs)

    @sdk_public_method
    def run_stream(self, output_temp_table: str) -> StreamingQuery:
        """
        Starts a streaming job to keep writting the output records of this FeatureView to a temporary table.
        The job will be running until the execution is terminated.

        After records have been written to the table, they can be queried using `spark.sql()`.
        If ran in a Databricks notebook, Databricks will also automatically visualize the number of incoming records.

        :param output_temp_table: The name of the temporary table to write to.

        Example:

            1) :py:mod:`fv.run_stream(output_temp_table="temp_table")` Start a streaming job.

            2) :py:mod:`display(spark.sql("SELECT * FROM temp_table LIMIT 5"))` Query the output table, and display the output dataframe.
        """
        return run_stream(self._proto, output_temp_table)


class StreamWindowAggregateFeatureView(FeatureView):
    """
    StreamFeatureView class.

    To get a FeatureView instance, call :py:func:`tecton.get_feature_view`.
    """

    @property  # type: ignore
    @sdk_public_method
    @is_documented_by(BatchWindowAggregateFeatureView.batch_materialization_schedule)
    def batch_materialization_schedule(self) -> Optional[pendulum.Duration]:
        return self._batch_materialization_schedule()

    @property  # type: ignore
    @sdk_public_method
    @is_documented_by(BatchWindowAggregateFeatureView.schedule_offset)
    def schedule_offset(self) -> Optional[pendulum.Duration]:
        return self._schedule_offset()

    @sdk_public_method
    @is_documented_by(BatchWindowAggregateFeatureView.materialization_status)
    def materialization_status(self, verbose=False, limit=1000, sort_columns=None, errors_only=False):
        return self._materialization_status(verbose, limit, sort_columns, errors_only)

    @property  # type: ignore
    @sdk_public_method
    @is_documented_by(BatchWindowAggregateFeatureView.type)
    def type(self) -> str:
        return "TemporalAggregate"

    @property  # type: ignore
    @sdk_public_method
    @is_documented_by(FeatureDefinition.features)
    def features(self) -> List[str]:
        return [f.output_feature_name for f in self._proto.temporal_aggregate.features]

    @sdk_public_method
    @is_documented_by(BatchWindowAggregateFeatureView.run)
    def run(
        self,
        feature_start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        feature_end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        aggregate_tiles: bool = None,
        aggregation_level: str = None,  # TODO(raviphol): Set this to "full" once aggregate_tiles is removed.
        **mock_inputs: Union[pandas.DataFrame, DataFrame],
    ) -> "tecton.interactive.data_frame.DataFrame":
        return run_batch(
            self._proto, feature_start_time, feature_end_time, mock_inputs, aggregate_tiles, aggregation_level
        )

    @sdk_public_method
    @is_documented_by(StreamFeatureView.run_stream)
    def run_stream(self, output_temp_table: str) -> StreamingQuery:
        run_stream(self._proto, output_temp_table)


class OnDemandFeatureView(FeatureView):
    """
    OnDemandFeatureView class.

    To get a FeatureView instance, call :py:func:`tecton.get_feature_view`.
    """

    @property  # type: ignore
    @sdk_public_method
    def type(self) -> str:
        """
        Returns the FeatureView type: 'OnDemand'.
        """
        return "OnDemand"

    @sdk_public_method
    def run(self, **mock_inputs: Union[pandas.DataFrame, DataFrame]) -> "tecton.interactive.data_frame.DataFrame":
        """
        Run the OnDemandFeatureView using the specified mock_inputs.

        :param mock_inputs: Required. All the FeatureView inputs must be provided. All dataframes must contain the
            same number of rows and their matching row ordering.

        Examples:
            A FeatureView 'fv' with inputs: 'ds1', 'ds2'.

            :py:mod:`fv.run(ds1=mock_dataframe1, ds2=mock_dataframe2)` Both ds1 and ds2 must be provided..

        :return: A tecton DataFrame of the results.
        """
        return run_ondemand(self._proto, self.name, mock_inputs)

    def _on_demand_transform_dataframe(
        self,
        spine: DataFrame,
        use_materialized_data: bool = True,
        namespace: Optional[str] = None,
    ) -> DataFrame:
        """
        Adds features from an OnDemandFeatureView to the spine.

        :param spine: Spark dataframe used to compute the on-demand features. Any dependent feature values must already be a part of the spine.
        :param use_materialized_data: (Optional) Use materialized data if materialization is enabled.

        :return: A spark dataframe containing the spine augmented with features. The features are prefixed by the namespace if it exists, or the FeatureView's name.
        """
        df = pipeline_helper.dataframe_with_input(
            pipeline=self._proto.pipeline,
            spark=TectonContext.get_instance()._spark,
            input_df=spine,
            output_schema=self._materialization_schema.to_spark(),
            transformations=self._proto.enrichments.transformations,
            name=self.name,
            fv_id=self.id,
            namespace=namespace,
        )
        return df

    def _should_infer_timestamp_of_spine(
        self, timestamp_key: Optional[str], spine: Optional[Union[pandas.DataFrame, DataFrame]]
    ):
        if timestamp_key is not None:
            return False
        if spine is None:
            return False
        # normally odfvs don't depend on a timestamp key except for when they have dependent fvs
        # in this case we want to infer the timestamp key of the spine. A dependent fv can't be a odfv.
        return utils.get_num_dependent_fv(self._proto.pipeline.root, visited_inputs={}) > 0

    @sdk_public_method
    def get_historical_features(
        self,
        spine: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, TectonDataFrame],
        timestamp_key: Optional[str] = None,
        from_source: bool = False,
        save: bool = False,
        save_as: Optional[str] = None,
    ) -> TectonDataFrame:
        """
        Returns a Tecton :class:`DataFrame` of historical values for this feature view.

        :param spine: The spine to join against, as a dataframe.
            The returned data frame will contain rollups for all (join key, request data key)
            combinations that are required to compute a full frame from the spine.
        :type spine: Union[pyspark.sql.DataFrame, pandas.DataFrame, tecton.DataFrame]
        :param timestamp_key: (Optional) Name of the time column in spine.
            This method will fetch the latest features computed before the specified timestamps in this column.
            If unspecified and this feature view has feature view dependencies, `timestamp_key` will default to the time column of the spine if there is only one present.
        :type timestamp_key: str
        :param from_source: (Optional) Whether feature values should be recomputed from the original data source.
            If False, we will read the materialized values from the offline store.
        :type from_source: bool
        :param save: (Optional) Whether to persist the DataFrame as a Dataset object. Default is False.
        :type save: bool
        :param save_as: (Optional) Name to save the DataFrame as. If unspecified and save=True, a name will be generated.
        :type: save_as: str

        Examples:
            An OnDemandFeatureView :py:mod:`fv` that expects request time data for the key :py:mod:`amount`.

            | The request time data is defined in the feature definition as such:
            | `request_schema = StructType()`
            | `request_schema.add(StructField('amount', DoubleType()))`
            | `transaction_request = RequestDataSource(request_schema=request_schema)`

            1) :py:mod:`fv.get_historical_features(spine)` where :py:mod:`spine=pandas.Dataframe({'amount': [30, 50, 10000]})`
            Fetch historical features from the offline store with request time data inputs 30, 50, and 10000 for key 'amount'.

            2) :py:mod:`fv.get_historical_features(spine, save_as='my_dataset')` where :py:mod:`spine=pandas.Dataframe({'amount': [30, 50, 10000]})`
            Fetch historical features from the offline store request time data inputs 30, 50, and 10000 for key 'amount'. Save the DataFrame as dataset with the name 'my_dataset'.

            An OnDemandFeatureView :py:mod:`fv` the expects request time data for the key :py:mod:`amount` and has a feature view dependency with join key :py:mod:`user_id`.

            1) :py:mod:`fv.get_historical_features(spine)` where :py:mod:`spine=pandas.Dataframe({'user_id': [1,2,3], 'date_1': [datetime(...), datetime(...), datetime(...)], 'amount': [30, 50, 10000]})`
            Fetch historical features from the offline store for users 1, 2, and 3 for the specified timestamps and values for `amount` in the spine.

        :return: A Tecton :class:`DataFrame`.
        """

        return self._get_historical_features(
            spine=spine,
            timestamp_key=timestamp_key,
            start_time=None,
            end_time=None,
            entities=None,
            from_source=from_source,
            save=save,
            save_as=save_as,
        )

    @sdk_public_method
    def get_online_features(
        self,
        join_keys: Optional[Mapping[str, Union[int, np.int_, str, bytes]]] = None,
        include_join_keys_in_response: bool = False,
        request_data: Optional[Mapping[str, Union[int, np.int_, str, bytes, float]]] = None,
    ) -> FeatureVector:
        """
        Returns a single Tecton :class:`FeatureVector` from the Online Store.
        At least one of join_keys or request_data is required.

        :param join_keys: Join keys of the enclosed FeatureViews.
        :param include_join_keys_in_response: Whether to include join keys as part of the response FeatureVector.
        :param request_data: Dictionary of request context values used for OnDemandFeatureViews.

          Examples:
            An OnDemandFeatureView :py:mod:`fv` that expects request time data for the key :py:mod:`amount`.

            | The request time data is defined in the feature definition as such:
            | `request_schema = StructType()`
            | `request_schema.add(StructField('amount', DoubleType()))`
            | `transaction_request = RequestDataSource(request_schema=request_schema)`

            1) :py:mod:`fv.get_online_features(request_data={'amount': 50})`
            Fetch the latest features with input amount=50.

            An OnDemandFeatureView :py:mod:`fv` that has a feature view dependency with join key :py:mod:`user_id` and expects request time data for the key :py:mod:`amount`.

            1) :py:mod:`fv.get_online_features(join_keys={'user_id': 1}, request_data={'amount': 50}, include_join_keys_in_respone=True)`
            Fetch the latest features from the online store for user 1 with input amount=50.
            In the returned FeatureVector, nclude the join key information (user_id=1).


        :return: A :class:`FeatureVector` of the results.
        """
        if join_keys is None and request_data is None:
            raise errors.GET_ONLINE_FEATURES_REQUIRED_ARGS
        if join_keys is None and utils.get_num_dependent_fv(self._proto.pipeline.root, visited_inputs={}) > 0:
            raise errors.GET_ONLINE_FEATURES_ODFV_JOIN_KEYS
        if join_keys is not None:
            utils.validate_join_key_types(join_keys)
        if request_data is not None and not isinstance(request_data, dict):
            raise errors.INVALID_REQUEST_DATA_TYPE(type(request_data))

        required_request_context_keys = list(self._request_context.arg_to_schema.keys())
        if len(required_request_context_keys) > 0 and request_data is None:
            raise errors.GET_ONLINE_FEATURES_FV_NO_REQUEST_DATA(required_request_context_keys)
        utils.validate_request_data(request_data, required_request_context_keys)

        return _QueryHelper(self._proto.fco_metadata.workspace, feature_view_name=self.name).get_feature_vector(
            join_keys or {},
            include_join_keys_in_response,
            request_data or {},
            self._request_context,
        )

    @property
    def _request_context(self) -> Optional[_RequestContext]:
        rc = find_request_context(self._proto.pipeline.root)
        return _RequestContext({}) if rc is None else _RequestContext._from_proto(rc)


@sdk_public_method
def get_feature_view(fv_reference: str, workspace_name: Optional[str] = None) -> FeatureView:
    """
    Fetch an existing :class:`FeatureView` by name.

    :param fv_reference: Either a name or a hexadecimal Feature View ID.
    :returns: :class:`BatchFeatureView`, :class:`BatchWindowAggregateFeatureView`,
        :class:`StreamFeatureView`, :class:`StreamWindowAggregateFeatureView`,
        or :class:`OnDemandFeatureView`.
    """
    request = GetFeatureViewRequest()
    request.version_specifier = fv_reference
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().GetFeatureView(request)
    if not response.HasField("feature_view"):
        raise errors.FCO_NOT_FOUND(FeatureView, fv_reference)

    if response.feature_view.HasField("feature_table"):
        raise errors.FCO_NOT_FOUND_WRONG_TYPE(FeatureView, fv_reference, "get_feature_table")

    return _get_feature_view_by_type(response.feature_view, fv_reference)


def _get_feature_view_by_type(feature_view_proto: feature_view_pb2.FeatureView, fv_reference: str):
    if feature_view_proto.HasField("on_demand_feature_view"):
        return OnDemandFeatureView(feature_view_proto)
    if feature_view_proto.HasField("temporal"):
        data_source_type = feature_view_proto.temporal.data_source_type
        if data_source_type == DataSourceType.BATCH:
            return BatchFeatureView(feature_view_proto)
        if data_source_type == DataSourceType.STREAM_WITH_BATCH:
            return StreamFeatureView(feature_view_proto)
        raise errors.INTERNAL_ERROR("Missing data_source_type for temporal FeatureView.")
    if feature_view_proto.HasField("temporal_aggregate"):
        data_source_type = feature_view_proto.temporal_aggregate.data_source_type
        if data_source_type == DataSourceType.BATCH:
            return BatchWindowAggregateFeatureView(feature_view_proto)
        if data_source_type == DataSourceType.STREAM_WITH_BATCH:
            return StreamWindowAggregateFeatureView(feature_view_proto)
        raise errors.INTERNAL_ERROR("Missing data_source_type for temporal aggregate FeatureView.")
    raise errors.INTERNAL_ERROR("Missing or unsupported FeatureView type.")
