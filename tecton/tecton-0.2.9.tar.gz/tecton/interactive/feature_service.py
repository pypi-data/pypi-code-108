import json
import time
from typing import List
from typing import Mapping
from typing import Optional
from typing import Union
from urllib.parse import urljoin

import numpy as np
import pandas
import pyspark
import pytimeparse
import requests
from google.protobuf.json_format import MessageToJson

import tecton
from tecton import conf
from tecton import LoggingConfig
from tecton._internals import data_frame_helper
from tecton._internals import errors
from tecton._internals import metadata_service
from tecton._internals.display import Displayable
from tecton._internals.feature_retrieval_internal import find_dependent_feature_set_items
from tecton._internals.sdk_decorators import sdk_public_method
from tecton._internals.utils import filter_internal_columns
from tecton._internals.utils import get_num_dependent_fv
from tecton._internals.utils import infer_timestamp
from tecton._internals.utils import is_live_workspace
from tecton._internals.utils import validate_join_key_types
from tecton._internals.utils import validate_request_data
from tecton._internals.utils import validate_spine_dataframe
from tecton.fco import Fco
from tecton.feature_services.query_helper import _QueryHelper
from tecton.interactive.data_frame import DataFrame
from tecton.interactive.data_frame import FeatureVector
from tecton.interactive.dataset import Dataset
from tecton.interactive.feature_set_config import FeatureSetConfig
from tecton.interactive.feature_table import FeatureTable
from tecton.interactive.feature_view import _get_feature_view_by_type
from tecton.interactive.feature_view import FeatureView
from tecton.tecton_context import TectonContext
from tecton_proto.api.featureservice.feature_service_pb2 import GetFeatureServiceStateRequest
from tecton_proto.data.feature_service_pb2 import FeatureService as FeatureServiceProto
from tecton_proto.metadataservice.metadata_service_pb2 import GetFeatureServiceRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetFeatureServiceSummaryRequest
from tecton_spark import snowflake_sql_helper
from tecton_spark.id_helper import IdHelper
from tecton_spark.logger import get_logger
from tecton_spark.transformation import _RequestContext

logger = get_logger("FeatureService")


class FeatureService(Fco):
    """
    FeatureService class.

    FeatureServices are used to serve feature values from :class:`FeatureView`. Users can use FeatureServices
    to make offline requests (e.g. to fetch a training dataset) using the :py:meth:`get_historical_features`
    method, and online requests (e.g. for online serving) using the :py:meth:`get_online_features`
    method. A FeatureService consists of a set of FeatureViews, plus configuration options.

    To get a FeatureService instance, call :py:func:`tecton.get_feature_service`.
    """

    proto: FeatureServiceProto
    feature_set_config: FeatureSetConfig
    _uri: str

    _query_helper: _QueryHelper

    def __init__(self):
        """ Do not call this directly. Use :py:func:`tecton.get_feature_service` """
        pass

    def __str__(self):
        return f"FeatureService|{self.name}"

    @classmethod
    def _from_proto(cls, feature_service: FeatureServiceProto):
        from tecton.interactive.feature_set_config import FeatureSetConfig

        obj = cls.__new__(cls)

        obj.proto = feature_service

        obj.feature_set_config = FeatureSetConfig._from_protos(feature_service.feature_set_items)

        # add dependent feature views into the FeatureSetConfig, uniquely per odfv
        # The namespaces of the dependencies have _udf_internal in the name and are filtered out before
        # being returned by TectonContext.execute()
        odfv_ids = set()
        for item in feature_service.feature_set_items:
            if item.enrichments.HasField("feature_view"):
                fv_id = IdHelper.to_string(item.feature_view_id)
                if fv_id in odfv_ids:
                    continue
                odfv_ids.add(fv_id)

                inputs = find_dependent_feature_set_items(
                    item.enrichments.feature_view.pipeline.root,
                    visited_inputs={},
                    fv_id=fv_id,
                    workspace_name=obj.workspace,
                )
                obj.feature_set_config._definitions_and_configs = (
                    obj.feature_set_config._definitions_and_configs + inputs
                )
                obj.feature_set_config._ondemand_input_definitions_and_configs = inputs

        return obj

    @classmethod
    def _fco_type_name_singular_snake_case(cls) -> str:
        return "feature_service"

    @classmethod
    def _fco_type_name_plural_snake_case(cls) -> str:
        return "feature_services"

    @property
    def _fco_metadata(self):
        return self.proto.fco_metadata

    @property  # type: ignore
    @sdk_public_method
    def feature_views(self) -> List[Union[FeatureView, FeatureTable]]:
        """
        Returns the Feature Views enclosed in this FeatureService.
        """
        fvs = []
        for d in self.feature_set_config.feature_definitions:
            if d.fv.HasField("feature_table"):
                fvs.append(FeatureTable(d.fv))
            else:
                fvs.append(_get_feature_view_by_type(d.fv, d.name))
        return fvs

    @property  # type: ignore
    @sdk_public_method
    def features(self) -> List[str]:
        """
        Returns the features generated by the enclosed feature views.
        """
        return self.feature_set_config.features

    @sdk_public_method
    def query_features(self, join_keys: Mapping[str, Union[np.int_, int, str, bytes]]) -> "tecton.DataFrame":
        """
        [Advanced Feature] Queries the FeatureService with a partial set of join_keys defined in the ``online_serving_index``
        of the included FeatureViews. Returns a Tecton :class:`DataFrame` of all matched records.

        :param join_keys: Query join keys, i.e., a union of join keys in the ``online_serving_index`` of all
            enclosed FeatureViews.
        :return: A Tecton :class:`DataFrame`
        """
        if not is_live_workspace(self.proto.fco_metadata.workspace):
            raise errors.UNSUPPORTED_OPERATION_IN_DEVELOPMENT_WORKSPACE("query_features")
        if not self.proto.online_serving_enabled:
            raise errors.UNSUPPORTED_OPERATION(
                "query_features", "online_serving_enabled was not defined for this Feature Service."
            )
        if not isinstance(join_keys, dict):
            raise errors.INVALID_JOIN_KEYS_TYPE(type(join_keys))

        return _QueryHelper(self.proto.fco_metadata.workspace, feature_service_name=self.name).query_features(join_keys)

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
            "Deprecated. Use the 'get_online_features' method instead to fetch features from the Online Store for this feature service. "
            + "See the api reference: https://docs.tecton.ai/api-reference/stubs/tecton.interactive.FeatureService.html#tecton.interactive.FeatureService.get_online_features"
        )
        if not self.proto.online_serving_enabled:
            raise errors.UNSUPPORTED_OPERATION(
                "get_feature_vector", "online_serving_enabled was not defined for this Feature Service."
            )
        if not join_keys and not request_context_map:
            raise errors.FS_GET_FEATURE_VECTOR_REQUIRED_ARGS
        if request_context_map is not None and not isinstance(request_context_map, dict):
            raise errors.INVALID_REQUEST_CONTEXT_TYPE(type(request_context_map))

        # do not require join_keys if all fvs are OnDemand with no dependent fvs
        if join_keys is None and not (
            all(
                (
                    fv.type == "OnDemand" and get_num_dependent_fv(fv._proto.pipeline.root, visited_inputs={}) == 0
                    for fv in self.feature_views
                )
            )
        ):
            raise errors.GET_FEATURE_VECTOR_FS_JOIN_KEYS
        # require request_data if there is an odfv in the FS
        if any((fv.type == "OnDemand" for fv in self.feature_views)):
            required_request_context_keys = list(self._request_context.arg_to_schema.keys())
            if len(required_request_context_keys) > 0 and request_context_map is None:
                raise errors.GET_FEATURE_VECTOR_FS_NO_REQUEST_DATA(required_request_context_keys)
            validate_request_data(request_context_map, required_request_context_keys, is_read_api_v3=False)

        return self.get_online_features(join_keys, include_join_keys_in_response, request_context_map)

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
        :param request_data: Dictionary of request context values. Only applicable when the FeatureService contains OnDemandFeatureViews.

        Examples:
            A FeatureService :py:mod:`fs` that contains a BatchFeatureView and StreamFeatureView with join keys :py:mod:`user_id` and :py:mod:`ad_id`.

            1) :py:mod:`fs.get_online_features(join_keys={'user_id': 1, 'ad_id': 'c234'})`
            Fetch the latest features from the online store for user 1 and ad 'c234'.

            2) :py:mod:`fv.get_online_features(join_keys={'user_id': 1, 'ad_id': 'c234'}, include_join_keys_in_respone=True)`
            Fetch the latest features from the online store for user 1 and ad id 'c234'. Include the join key information (user_id=1, ad_id='c234') in the returned FeatureVector.

            A FeatureService :py:mod:`fs_on_demand` that contains only OnDemandFeatureViews and expects request time data for key :py:mod:`amount`.

            | The request time data is defined in the feature definition as such:
            | `request_schema = StructType()`
            | `request_schema.add(StructField('amount', DoubleType()))`
            | `transaction_request = RequestDataSource(request_schema=request_schema)`

            1) :py:mod:`fs.get_online_features(request_data={'amount': 30})`
            Fetch the latest features from the online store with amount = 30.

            A FeatureService :py:mod:`fs_all` that contains feature views of all types with join key :py:mod:`user_id` and expects request time data for key :py:mod:`amount`.

            1) :py:mod:`fs.get_online_features(join_keys={'user_id': 1}, request_data={'amount': 30})`
            Fetch the latest features from the online store for user 1 with amount = 30.

        :return: A :class:`FeatureVector` of the results.
        """
        if not self.proto.online_serving_enabled:
            raise errors.UNSUPPORTED_OPERATION(
                "get_online_features", "online_serving_enabled was not defined for this Feature Service."
            )
        if not join_keys and not request_data:
            raise errors.FS_GET_ONLINE_FEATURES_REQUIRED_ARGS
        if join_keys is not None:
            validate_join_key_types(join_keys)
        if request_data is not None and not isinstance(request_data, dict):
            raise errors.INVALID_REQUEST_DATA_TYPE(type(request_data))

        # do not require join_keys if all fvs are OnDemand with no dependent fvs
        if join_keys is None and not (
            all(
                (
                    fv.type == "OnDemand" and get_num_dependent_fv(fv._proto.pipeline.root, visited_inputs={}) == 0
                    for fv in self.feature_views
                )
            )
        ):
            raise errors.GET_ONLINE_FEATURES_FS_JOIN_KEYS

        # require request_data param if there are request context keys
        required_request_context_keys = list(self._request_context.arg_to_schema.keys())
        if len(required_request_context_keys) > 0 and request_data is None:
            raise errors.GET_ONLINE_FEATURES_FS_NO_REQUEST_DATA(required_request_context_keys)
        validate_request_data(request_data, required_request_context_keys)

        return _QueryHelper(self.proto.fco_metadata.workspace, feature_service_name=self.name).get_feature_vector(
            join_keys or {},
            include_join_keys_in_response,
            request_data or {},
            self._request_context,
        )

    @sdk_public_method
    def get_feature_dataframe(
        self,
        spine: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, None],
        timestamp_key: Optional[str] = None,
        include_feature_view_timestamp_columns: bool = False,
        use_materialized_data: bool = True,
        save: bool = None,
        save_as: str = None,
    ) -> DataFrame:
        """
        Deprecated.
        Fetch a :class:`DataFrame` of feature values from this FeatureService.

        This method will return feature values for each row provided in the spine DataFrame. The feature values
        returned by this method will respect the timestamp provided in the timestamp column of the Spine DataFrame.

        This method fetches features from the Offline Store. If ``use_materialized_data==False``, feature values
        will instead be computed on the fly from raw data.

        :param spine: A dataframe of join keys and timestamps that specify which feature values to fetch.
        :param timestamp_key: Name of the time column in the spine dataframe. This column must be of type Spark timestamp.
        :param include_feature_view_timestamp_columns: (Optional) Include timestamp columns for each FeatureView in the FeatureService.
        :param use_materialized_data: (Optional) Use materialized data if materialization is enabled.
        :param save: (Optional) set to True to persist DataFrame as a Dataset object
        :param save_as: (Optional) name to save the DataFrame as. Not applicable when save=False.
            If unspecified and save=True, a name will be generated.
        :return: A Tecton :class:`DataFrame`.
        """
        logger.warning(
            "Deprecated. Use the 'get_historical_features' method instead to view historical values for this feature service."
            + "See the api reference: https://docs.tecton.ai/api-reference/stubs/tecton.interactive.FeatureService.html#tecton.interactive.FeatureService.get_historical_features"
        )
        # handling case where spine is None (note we don't allow the spine to be none in fs.get_historical_features)
        if spine is None:
            TectonContext.validate_spine_type(spine)
            if timestamp_key is None:
                keys = [fv.timestamp_key for fv in self.feature_views if not fv.is_on_demand]
                if len(keys) > 0:
                    if not all([key == keys[0] for key in keys]):
                        raise errors.FS_AMBIGUOUS_TIMESTAMP_KEY(keys)
                    timestamp_key = keys[0]

            df = self.feature_set_config.get_feature_dataframe(
                spine,
                timestamp_key=timestamp_key,
                include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
                use_materialized_data=use_materialized_data,
            )
            if save or save_as is not None:
                return Dataset._create(
                    df=df,
                    save_as=save_as,
                    workspace=self.workspace,
                    feature_service_id=self.id,
                    timestamp_key=timestamp_key,
                )
            return df
        # check here instead of get_historical_features so error includes correct param name
        if (
            any(fv.type == "FeatureTable" for fv in self.feature_views)
            and is_live_workspace(self.workspace)
            and not use_materialized_data
        ):
            raise errors.USE_MATERIALIZED_DATA_WITH_FT

        return self.get_historical_features(
            spine, timestamp_key, include_feature_view_timestamp_columns, not use_materialized_data, save, save_as
        )

    @sdk_public_method
    def get_historical_features(
        self,
        spine: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, DataFrame, str],
        timestamp_key: Optional[str] = None,
        include_feature_view_timestamp_columns: bool = False,
        from_source: bool = False,
        save: bool = False,
        save_as: Optional[str] = None,
    ) -> DataFrame:
        """
        Fetch a :class:`DataFrame` of feature values from this FeatureService.

        This method will return feature values for each row provided in the spine DataFrame. The feature values
        returned by this method will respect the timestamp provided in the timestamp column of the spine DataFrame.

        This method fetches features from the Offline Store. If ``from_source=True``, feature values
        will instead be computed on the fly from raw data.

        :param spine: A dataframe of possible join keys, request data keys, and timestamps that specify which feature values to fetch.To distinguish
            between spine columns and feature columns, feature columns are labeled as `feature_view_name.feature_name`
            in the returned DataFrame.
        :type spine: Union[pyspark.sql.DataFrame, pandas.DataFrame, tecton.DataFrame]
        :param timestamp_key: (Optional) Name of the time column in the spine DataFrame.
            This method will fetch the latest features computed before the specified timestamps in this column.
            Not applicable if the FeatureService stricly contains OnDemandFeatureViews with no feature view dependencies.
        :type timestamp_key: str
        :param include_feature_view_timestamp_columns: (Optional) Whether to include timestamp columns for each FeatureView in the FeatureService. Default is False.
        :type include_feature_view_timestamp_columns: bool
        :param from_source: (Optional) Whether feature values should be recomputed from the original data source.
            If False, we will read the values from the materialized Offline store.
        :type from_source: bool
        :param save: (Optional) Whether to persistthe  DataFrame as a Dataset object. Default is False.
        :type save: bool
        :param save_as: (Optional) Name to save the DataFrame as.
            If unspecified and save=True, a name will be generated.
        :type save_as: str

        Examples:
            A FeatureService :py:mod:`fs` that contains a BatchFeatureView and StreamFeatureView with join keys :py:mod:`user_id` and :py:mod:`ad_id`.

            1) :py:mod:`fs.get_historical_features(spine)` where :py:mod:`spine=pandas.Dataframe({'user_id': [1,2,3], 'ad_id': ['a234', 'b256', 'c9102'], 'date': [datetime(...), datetime(...), datetime(...)]})`
            Fetch historical features from the offline store for users 1, 2, and 3 for the specified timestamps and ad ids in the spine.

            2) :py:mod:`fs.get_historical_features(spine, save_as='my_dataset)` where :py:mod:`spine=pandas.Dataframe({'user_id': [1,2,3], 'ad_id': ['a234', 'b256', 'c9102'], 'date': [datetime(...), datetime(...), datetime(...)]})`
            Fetch historical features from the offline store for users 1, 2, and 3 for the specified timestamps and ad ids in the spine. Save the DataFrame as dataset with the name :py:mod:`my_dataset`.

            3) :py:mod:`fv.get_historical_features(spine, timestamp_key='date_1')` where :py:mod:`spine=pandas.Dataframe({'user_id': [1,2,3], 'ad_id': ['a234', 'b256', 'c9102'],
            'date_1': [datetime(...), ...], 'date_2': [datetime(...), ...]})`
            Fetch historical features from the offline store for users 1, 2, and 3 for the ad ids and specified timestamps in the :py:mod:`date_1` column in the spine.

            A FeatureService :py:mod:`fs_on_demand` that contains only OnDemandFeatureViews and expects request time data for the key :py:mod:`amount`.

            | The request time data is defined in the feature definition as such:
            | `request_schema = StructType()`
            | `request_schema.add(StructField('amount', DoubleType()))`
            | `transaction_request = RequestDataSource(request_schema=request_schema)`

            1) :py:mod:`fs_on_demand.get_historical_features(spine)` where :py:mod:`spine=pandas.Dataframe({'amount': [30, 50, 10000]})`
            Fetch historical features from the offline store with request data inputs 30, 50, and 10000.

            A FeatureService :py:mod:`fs_all` that contains feature views of all types with join key 'user_id' and expects request time data for the key :py:mod:`amount`.

            1) :py:mod:`fs_all.get_historical_features(spine)` where :py:mod:`spine=pandas.Dataframe({'user_id': [1,2,3], 'amount': [30, 50, 10000], 'date': [datetime(...), datetime(...), datetime(...)]})`
            Fetch historical features from the offline store for users 1, 2, and 3 for the specified timestamps and request data inputs in the spine.

        :return: A Tecton :class:`DataFrame`.
        """
        if conf.get_or_none("ALPHA_SNOWFLAKE_COMPUTE_ENABLED"):
            # TODO: We probably need to do some validation here before running everything
            return DataFrame._create(
                snowflake_sql_helper.get_historical_features(
                    spine=spine,
                    timestamp_key=timestamp_key,
                    feature_set_items=[item for item in self.proto.feature_set_items],
                    # This is a hack to get around the dependency from interactive to tecton_spark.
                    ondemand_feature_set_items=[
                        config.to_proto()
                        for config in self.feature_set_config._get_ondemand_feature_definitions_and_join_configs()
                    ],
                    username=conf.get_or_raise("SNOWFLAKE_USER"),
                    password=conf.get_or_raise("SNOWFLAKE_PASSWORD"),
                )
            )
        # str is only supported for Snowflake
        if isinstance(spine, str):
            raise TypeError(
                "spine must be one of (pyspark.sql.dataframe.DataFrame, pandas.core.frame.DataFrame, tecton.interactive.data_frame.DataFrame); got str instead"
            )

        if any(fv.type == "FeatureTable" for fv in self.feature_views):
            if not is_live_workspace(self.workspace):
                raise errors.FS_WITH_FT_DEVELOPMENT_WORKSPACE
            elif from_source:
                raise errors.FROM_SOURCE_WITH_FT

        spark = TectonContext.get_instance()._spark
        if isinstance(spine, pandas.DataFrame):
            spine = spark.createDataFrame(spine)
        elif isinstance(spine, DataFrame):
            spine = spine.to_spark()

        timestamp_required = any(
            [fv._should_infer_timestamp_of_spine(timestamp_key, spine) for fv in self.feature_views]
        )

        if timestamp_required:
            timestamp_key = timestamp_key or infer_timestamp(spine)
        validate_spine_dataframe(spine, timestamp_key, list(self._request_context.arg_to_schema.keys()))

        df = data_frame_helper.get_features_for_spine(
            spark,
            spine,
            self.feature_set_config,
            timestamp_key=timestamp_key,
            from_source=from_source,
            include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
        )
        df = filter_internal_columns(df)
        df = DataFrame._create(df)
        if save or save_as is not None:
            return Dataset._create(
                df=df,
                save_as=save_as,
                workspace=self.workspace,
                feature_service_id=self.id,
                spine=spine,
                timestamp_key=timestamp_key,
            )
        return df

    # TODO: Change this to a @sdk_public_method once it's fully ready.
    def _get_feature_sql_str(
        self,
        spine_sql: Optional[str] = None,
        timestamp_key: Optional[str] = None,
        include_feature_view_timestamp_columns: bool = False,
    ) -> str:
        """
        Fetch a SQL str to retrive feature values from this FeatureService. Currently this method only supports Snowflake SQL pipeline.
        spine_sql and spine_table_name cannot be both empty.

        :param spine_sql: SQL str to get the spine.
        :param spine_table_name: Spine table name to get the spine.
        :param timestamp_key: Name of the time column in the spine dataframe. This column must be of type Spark timestamp.
        :param include_feature_view_timestamp_columns: (Optional) Include timestamp columns for each FeatureView in the FeatureService.
        :return: A SQL str that can be used to fetch feature values
        """
        # TODO: Validate if the Feature Views in the FeatureService are supported types
        if timestamp_key is None:
            keys = [fv.timestamp_key for fv in self.feature_views if not fv.is_on_demand]
            if len(keys) > 0:
                if not all([key == keys[0] for key in keys]):
                    raise errors.FS_AMBIGUOUS_TIMESTAMP_KEY(keys)
                timestamp_key = keys[0]

        return snowflake_sql_helper.get_features_sql_str_for_spine(
            spine_sql=spine_sql,
            timestamp_key=timestamp_key,
            feature_set_items=self.proto.feature_set_items,
            include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
        )

    @sdk_public_method
    def wait_until_ready(self, timeout="15m", wait_for_materialization=True, verbose=False):
        """Blocks until the service is ready to serve real-time requests.

        The FeatureService is considered ready once every FeatureView that has been added to it
        has had at least once successful materialization run.

        :param timeout: Timeout string.
        :param wait_for_materialization: If False, does not wait for batch materialization to complete.
        """
        if not is_live_workspace(self.proto.fco_metadata.workspace):
            raise errors.UNSUPPORTED_OPERATION_IN_DEVELOPMENT_WORKSPACE("wait_until_ready")

        timeout_seconds = pytimeparse.parse(timeout)
        deadline = time.time() + timeout_seconds

        has_been_not_ready = False
        while True:
            request = GetFeatureServiceStateRequest()
            request.feature_service_locator.feature_service_name = self.name
            request.feature_service_locator.workspace_name = self.proto.fco_metadata.workspace
            http_response = requests.post(
                urljoin(conf.get_or_raise("FEATURE_SERVICE") + "/", "v1/feature-service/get-feature-service-state"),
                data=MessageToJson(request),
                headers=_QueryHelper(
                    self.proto.fco_metadata.workspace, feature_service_name=self.name
                )._prepare_headers(),
            )
            details = http_response.json()
            if http_response.status_code == 404:
                # FeatureService is not ready to serve
                if verbose:
                    logger.info(f" Waiting for FeatureService to be ready to serve ({details['message']})")
                else:
                    logger.info(f" Waiting for FeatureService to be ready to serve")
            elif http_response.status_code == 200:
                # FeatureService is ready
                if verbose:
                    logger.info(f"wait_until_ready: Ready! Response={http_response.text}")
                else:
                    logger.info(f"wait_until_ready: Ready!")
                # Extra wait time due to different FS hosts being potentially out-of-sync in picking up the latest state
                if has_been_not_ready:
                    time.sleep(20)
                return
            else:
                http_response.raise_for_status()
                return
            if time.time() > deadline:
                logger.info(f"wait_until_ready: Response={http_response.text}")
                raise TimeoutError()
            has_been_not_ready = True
            time.sleep(10)
            continue

    @sdk_public_method
    def summary(self) -> Displayable:
        """
        Returns various information about this FeatureService, including the most critical metadata such
        as the FeatureService's name, owner, features, etc.
        """
        return Displayable.from_items(headings=["Property", "Value"], items=self._summary_items())

    @property  # type: ignore
    @sdk_public_method
    def id(self) -> str:
        """
        Legacy attribute. Use name to refer to a FeatureService.
        """
        return IdHelper.to_string(self.proto.feature_service_id)

    def _summary_items(self):
        request = GetFeatureServiceSummaryRequest()
        request.feature_service_id.CopyFrom(self.proto.feature_service_id)
        request.workspace = self.workspace
        response = metadata_service.instance().GetFeatureServiceSummary(request)
        items_map = {}
        summary_items = []
        for item in response.general_items:
            items_map[item.key] = item
            if item.display_name:
                summary_items.append((item.display_name, item.multi_values if item.multi_values else item.value))

        if "curlEndpoint" in items_map and "curlParamsJson" in items_map:
            api_service = conf.get_or_none("API_SERVICE")
            assert api_service is not None, "API_SERVICE must be configured"
            if "localhost" not in api_service and "ingress" not in api_service:
                assert api_service.endswith(
                    "/api"
                ), "API_SERVICE should look like https://<deployment-name>.tecton.ai/api"
            service_url = urljoin(api_service, items_map["curlEndpoint"].value)
            curl_params_json = json.dumps(json.loads(items_map["curlParamsJson"].value), indent=2)
            curl_header = items_map["curlHeader"].value
            curl_str = "curl -X POST " + service_url + '\\\n-H "' + curl_header + "\"-d\\\n'" + curl_params_json + "'"
            summary_items.append(("Example Curl", curl_str))
        return summary_items

    @property
    def _request_context(self):
        merged_context = _RequestContext({})
        for fv in self.feature_views:
            if fv.type == "OnDemand":
                merged_context._merge(fv._request_context)
        return merged_context

    @property
    def logging(self) -> Optional["LoggingConfig"]:
        """
        Returns the logging configuration of this FeatureService.
        """
        return LoggingConfig._from_proto(self.proto.logging)


@sdk_public_method
def get_feature_service(name: str, workspace_name: Optional[str] = None) -> FeatureService:
    """
    Fetch an existing :class:`FeatureService` by name.

    :param name: Name or string ID of the :class:`FeatureService`.
    :return: An instance of :class:`FeatureService`.
    """
    request = GetFeatureServiceRequest()
    request.service_reference = name
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().GetFeatureService(request)

    if not response.HasField("feature_service"):
        raise errors.FCO_NOT_FOUND(FeatureService, name)

    return FeatureService._from_proto(response.feature_service)
