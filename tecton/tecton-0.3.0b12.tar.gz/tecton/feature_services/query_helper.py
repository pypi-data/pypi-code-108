from datetime import datetime
from json import JSONDecodeError
from typing import Dict
from typing import Mapping
from typing import Optional
from typing import Union
from urllib.parse import urljoin

import numpy as np
import pandas as pd
import requests
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.struct_pb2 import Value
from pyspark.sql.types import ArrayType
from pyspark.sql.types import BooleanType
from pyspark.sql.types import DoubleType
from pyspark.sql.types import FloatType
from pyspark.sql.types import LongType
from pyspark.sql.types import StringType
from requests.exceptions import HTTPError

import tecton
from tecton import conf
from tecton._internals import errors
from tecton.interactive.data_frame import FeatureVector
from tecton_proto.api.featureservice.feature_service_pb2 import FeatureServerComplexDataType
from tecton_proto.api.featureservice.feature_service_pb2 import FeatureServerDataType
from tecton_proto.api.featureservice.feature_service_pb2 import GetFeaturesResponse
from tecton_proto.api.featureservice.feature_service_pb2 import GetFeaturesResult
from tecton_proto.api.featureservice.feature_service_pb2 import Metadata
from tecton_proto.api.featureservice.feature_service_pb2 import QueryFeaturesRequest
from tecton_proto.api.featureservice.feature_service_pb2 import QueryFeaturesResponse
from tecton_proto.api.featureservice.feature_service_request_pb2 import GetFeaturesRequest
from tecton_spark.transformation import _RequestContext

TYPE_BOOLEAN = "boolean"
TYPE_FLOAT64 = "float64"
TYPE_INT64 = "int64"
TYPE_STRING = "string"
TYPE_STRING_ARRAY = "string_array"
TYPE_NULL_VALUE = "null_value"
TYPE_ERROR = "error"


class _QueryHelper:
    def __init__(
        self,
        workspace_name: str,
        feature_service_name: Optional[str] = None,
        feature_view_name: Optional[str] = None,
    ):
        assert (feature_service_name is not None) ^ (feature_view_name is not None)
        self.workspace_name = workspace_name
        self.feature_service_name = feature_service_name
        self.feature_view_name = feature_view_name

    def _prepare_headers(self) -> Dict[str, str]:
        token = conf.get_or_none("TECTON_API_KEY")
        if not token:
            raise errors.FS_API_KEY_MISSING

        return {"authorization": f"Tecton-key {token}"}

    def query_features(self, join_keys: Mapping[str, Union[int, np.int_, str, bytes]]) -> "tecton.DataFrame":
        """
        Queries the FeatureService with partial set of join_keys defined in the OnlineServingIndex
        of the enclosed feature definitions. Returns feature vectors for all matched records.
        See OnlineServingIndex.

        :param join_keys: Query join keys, i.e., a union of join keys in OnlineServingIndex of all
            enclosed feature definitions.
        :return: A Tecton DataFrame
        """
        request = QueryFeaturesRequest()
        self._prepare_request_params(request.params, join_keys)
        http_response = requests.post(
            urljoin(conf.get_or_raise("FEATURE_SERVICE") + "/", "v1/feature-service/query-features"),
            data=MessageToJson(request),
            headers=self._prepare_headers(),
        )

        self._detailed_http_raise_for_status(http_response)

        response = QueryFeaturesResponse()
        Parse(http_response.text, response, True)

        pandas_df = self._query_response_to_pandas(response, join_keys)

        import tecton

        return tecton.DataFrame._create(pandas_df)

    def get_feature_vector(
        self,
        join_keys: Mapping[str, Union[int, np.int_, str, bool]],
        include_join_keys_in_response: bool,
        request_context_map: Mapping[str, Union[int, np.int_, str, float, bool]],
        request_context_schema: _RequestContext,
    ) -> FeatureVector:
        """
        Returns a single Tecton FeatureVector.

        :param join_keys: Join keys of the enclosed feature definitions.
        :param include_join_keys_in_response: Whether to include join keys as part of the response FeatureVector.
        :param request_context_map: Dictionary of request context values.

        :return: A FeatureVector of the results.
        """
        request = GetFeaturesRequest()
        self._prepare_request_params(request.params, join_keys, request_context_map, request_context_schema)

        http_response = requests.post(
            urljoin(conf.get_or_raise("FEATURE_SERVICE") + "/", "v1/feature-service/get-features"),
            data=MessageToJson(request),
            headers=self._prepare_headers(),
        )

        self._detailed_http_raise_for_status(http_response)

        response = GetFeaturesResponse()
        Parse(http_response.text, response, True)

        return self._response_to_feature_vector(response, include_join_keys_in_response, join_keys)

    def _response_to_feature_vector(
        self,
        response: GetFeaturesResponse,
        include_join_keys: bool,
        join_keys: Dict,
    ) -> FeatureVector:
        features = {}
        if include_join_keys:
            for k, v in join_keys.items():
                features[k] = v

        features.update(self._feature_dict(response.result, response.metadata))
        metadata_values = self._prepare_metadata_response(response.metadata)
        return FeatureVector(
            names=list(features.keys()),
            values=list(features.values()),
            effective_times=[metadata_values["effective_time"].get(name) for name in features.keys()],
            slo_info=metadata_values["slo_info"],
        )

    def _prepare_metadata_response(self, metadata: Metadata) -> (Dict[str, dict]):
        metadata_values = {}
        metadata_values["slo_info"] = MessageToDict(metadata.slo_info)

        times = {}
        for i, feature in enumerate(metadata.features):
            time = metadata.features[i].effective_time
            time = datetime.utcfromtimestamp(time.seconds)
            times[metadata.features[i].name] = time

        metadata_values["effective_time"] = times
        return metadata_values

    def _feature_dict(self, result: GetFeaturesResult, metadata: Metadata) -> Dict[str, Union[int, str, float, list]]:
        values = {}
        for i, feature in enumerate(result.features):
            values[metadata.features[i].name] = self._pb_to_python_value(feature, metadata.features[i].data_type)

        for i, jk in enumerate(result.join_keys):
            values[metadata.join_keys[i].name] = self._pb_to_python_value(jk, metadata.join_keys[i].data_type)
        return values

    def _prepare_request_params(self, params, join_keys, request_context_map=None, request_context_schema=None):
        request_context = request_context_map or {}

        # always returning all the metadata
        params.metadata_options.include_names = True
        params.metadata_options.include_data_types = True
        params.metadata_options.include_effective_times = True
        params.metadata_options.include_slo_info = True

        if self.feature_service_name is not None:
            params.feature_service_name = self.feature_service_name
        elif self.feature_view_name is not None:
            params.feature_view_name = self.feature_view_name
        params.workspace_name = self.workspace_name

        for k, v in join_keys.items():
            self._python_to_pb_value(k, params.join_key_map[k], v)
        for k, v in request_context.items():
            schema_type = request_context_schema.arg_to_schema.get(k, None)
            # Validate request context key
            if schema_type is None:
                raise errors.UNKNOWN_REQUEST_CONTEXT_KEY(sorted(request_context_schema.arg_to_schema.keys()), k)
            self._request_context_to_pb_value(k, params.request_context_map[k], v, schema_type)

    def _detailed_http_raise_for_status(self, http_response):
        try:
            http_response.raise_for_status()
        except HTTPError as e:
            try:
                details = http_response.json()
            except JSONDecodeError as json_e:
                raise errors.FS_BACKEND_ERROR(f"unable to process response ({http_response.status_code} error)")

            # Include the actual error message details in the exception
            # if available.
            if "message" in details and "code" in details:
                raise errors.FS_BACKEND_ERROR(details["message"])
            else:
                # Otherwise just throw the original error.
                raise e

    def _query_response_to_pandas(
        self, response: QueryFeaturesResponse, join_keys: Mapping[str, Union[int, np.int_, str, bytes]]
    ):
        response_count = len(response.results)
        data = {key: [value] * response_count for key, value in join_keys.items()}
        for result in response.results:
            features = self._feature_dict(result, response.metadata)
            # note that int(1) = np.int_(1) so dict lookup works here
            for k, v in features.items():
                if k not in data.keys():
                    data[k] = []
                data[k] = list(data[k]) + [v]  # type: ignore
        return pd.DataFrame(data=data)

    def _pb_to_python_value(self, v: Value, data_type: FeatureServerComplexDataType):
        """Converts a "Value" wrapped value into the type indicated by "type"."""
        which = v.WhichOneof("kind")
        if which is None or which == TYPE_NULL_VALUE:
            return None
        val = getattr(v, which)

        if data_type.type in (FeatureServerDataType.string, FeatureServerDataType.boolean):
            return val
        elif data_type.type in (FeatureServerDataType.float64, FeatureServerDataType.float32):
            return float(val)
        elif data_type.type == FeatureServerDataType.int64:
            # The feature server returns int64s as strings, which need to be cast.
            return int(val)
        elif data_type.type == FeatureServerDataType.array:
            return [self._pb_to_python_value(vi, data_type.element_type) for vi in val.values]
        else:
            raise Exception(f"Unexpected type '{data_type}' - Expected float64, int64, string, boolean, or array")

    def _python_to_pb_value(
        self, key: str, api_value: "Value", python_value: Union[int, np.int_, str, bool], schema_type=None
    ):
        """Converts a single value from a python type to a protobuf wrapped value. Cast to type passed in param or infer based on python type."""

        # NB. bool is a subclass of int in Python for some weird reason so we check for it first
        if isinstance(python_value, bool):
            api_value.bool_value = python_value
        elif isinstance(python_value, int):
            api_value.string_value = str(python_value)
        elif isinstance(python_value, np.int_):
            api_value.string_value = str(python_value)
        elif isinstance(python_value, str):
            api_value.string_value = python_value
        else:
            raise NotImplementedError(
                f"Found type '{type(python_value).__name__} for {key}' - Expected one of int, str, bool"
            )

    def _request_context_to_pb_value(
        self, key: str, api_value: "Value", python_value: Union[int, np.int_, str, bool, float, list], schema_type
    ):
        if python_value is None:
            api_value.null_value = True
        elif schema_type == BooleanType():
            if not isinstance(python_value, bool):
                raise TypeError(f"Invalid type for {key}: expected bool, got {type(python_value).__name__}")
            api_value.bool_value = python_value
        elif schema_type == LongType():
            if not (isinstance(python_value, int) or isinstance(python_value, np.int_)):
                raise TypeError(
                    f"Invalid type for {key}: expected int or numpy.int_, got {type(python_value).__name__}"
                )
            api_value.string_value = str(python_value)
        elif schema_type == StringType():
            if not isinstance(python_value, str):
                raise TypeError(f"Invalid type for {key}: expected str, got {type(python_value).__name__}")
            api_value.string_value = python_value
        elif schema_type in (DoubleType(), FloatType()):
            if not (
                isinstance(python_value, int) or isinstance(python_value, float) or isinstance(python_value, np.int_)
            ):
                raise TypeError(f"Invalid type for {key}: expected int or float, got {type(python_value).__name__}")
            api_value.number_value = python_value
        elif isinstance(schema_type, ArrayType):
            if not isinstance(python_value, list):
                raise TypeError(f"Invalid type for {key}: expected list, got {type(python_value).__name__}")
            api_value.list_value.SetInParent()  # Needed in the case of empty arrays.
            for item in python_value:
                list_value = api_value.list_value.values.add()
                self._request_context_to_pb_value(key + ".elementType", list_value, item, schema_type.elementType)
        else:
            # should never happen
            raise NotImplementedError(f"Schema type {schema_type} not supported")

        return schema_type
