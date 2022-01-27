from datetime import datetime
from io import BytesIO
from typing import Mapping
from typing import Optional
from typing import Union

import numpy as np
import pandas
import pendulum
import pyspark
import requests
from pyspark.sql.types import ArrayType
from pyspark.sql.types import DoubleType
from pyspark.sql.types import FloatType
from pyspark.sql.types import IntegerType
from pyspark.sql.types import LongType
from pyspark.sql.types import StructType

from tecton import conf
from tecton._internals import errors
from tecton._internals import metadata_service
from tecton._internals.sdk_decorators import sdk_public_method
from tecton._internals.utils import validate_join_key_types
from tecton.feature_services.query_helper import _QueryHelper
from tecton.interactive.data_frame import DataFrame
from tecton.interactive.data_frame import FeatureVector
from tecton.interactive.feature_definition import FeatureDefinition
from tecton.tecton_context import TectonContext
from tecton_proto.data import feature_view_pb2
from tecton_proto.metadataservice.metadata_service_pb2 import GetFeatureViewRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetNewIngestDataframeInfoRequest
from tecton_proto.metadataservice.metadata_service_pb2 import IngestDataframeRequest
from tecton_spark.logger import get_logger
from tecton_spark.schema import Schema

logger = get_logger("FeatureTable")

__all__ = ["FeatureTable", "get_feature_table"]


class FeatureTable(FeatureDefinition):
    """
    FeatureTable class.

    To get a FeatureTable instance, call :py:func:`tecton.get_feature_table`.
    """

    _proto: feature_view_pb2.FeatureView

    def __init__(self, proto):
        self._proto = proto

    @classmethod
    def _fco_type_name_singular_snake_case(cls) -> str:
        return "feature_table"

    @classmethod
    def _fco_type_name_plural_snake_case(cls) -> str:
        return "feature_tables"

    def __str__(self):
        return f"FeatureTable|{self.id}"

    def __repr__(self):
        return f"FeatureTable(name='{self.name}')"

    @property  # type: ignore
    @sdk_public_method
    def type(self) -> str:
        """
        Returns the FeatureTable type.
        """
        return "FeatureTable"

    def timestamp_key(self) -> str:
        """
        Returns the timestamp_key column name of this FeatureTable.
        """
        return self._proto.timestamp_key

    @sdk_public_method
    def get_features(
        self,
        entities: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, None] = None,
        start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
    ) -> DataFrame:
        """
        Deprecated.
        Gets all features that are defined by this FeatureTable.

        :param entities: (Optional) A DataFrame that is used to filter down feature values.
            If specified, this DataFrame should only contain join key columns.
        :param start_time: (Optional) The interval start time from when we want to retrieve features.
        :param end_time:  (Optional) The interval end time until when we want to retrieve features.

        :return: A Tecton DataFrame with features values.
        """
        logger.warning(
            "Deprecated. Use the 'get_historical_features' method instead to view historical values for this feature table. "
            + "See the api reference: https://docs.tecton.ai/api-reference/stubs/tecton.interactive.FeatureTable.html#tecton.interactive.FeatureTable.get_historical_features"
        )

        return self.get_historical_features(start_time=start_time, end_time=end_time, entities=entities)

    @sdk_public_method
    def get_historical_features(
        self,
        spine: Optional[Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, DataFrame]] = None,
        timestamp_key: Optional[str] = None,
        entities: Optional[Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, DataFrame]] = None,
        start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        save: bool = False,
        save_as: Optional[str] = None,
    ) -> DataFrame:
        """
        Returns a Tecton :class:`DataFrame` of historical values for this feature table.
        If no arguments are passed in, all feature values for this feature table will be returned in a Tecton DataFrame.
        Note:
        The `timestamp_key` parameter is only applicable when a spine is passed in.
        Parameters `start_time`, `end_time`, and `entities` are only applicable when a spine is not passed in.

        :param spine: (Optional) The spine to join against, as a dataframe.
            If present, the returned DataFrame will contain rollups for all (join key, temporal key)
            combinations that are required to compute a full frame from the spine.
            To distinguish between spine columns and feature columns, feature columns are labeled as
            `feature_view_name.feature_name` in the returned DataFrame.
            If spine is not specified, it'll return a DataFrame of  feature values in the specified time range.
        :type spine: Union[pyspark.sql.DataFrame, pandas.DataFrame, tecton.DataFrame]
        :param timestamp_key: (Optional) Name of the time column in spine.
            This method will fetch the latest features computed before the specified timestamps in this column.
            If unspecified, will default to the time column of the spine if there is only one present.
        :type timestamp_key: str
        :param entities: (Optional) A DataFrame that is used to filter down feature values.
            If specified, this DataFrame should only contain join key columns.
        :type entities: Union[pyspark.sql.DataFrame, pandas.DataFrame, tecton.DataFrame]
        :param start_time: (Optional) The interval start time from when we want to retrieve features.
            If no timezone is specified, will default to using UTC.
        :type start_time: Union[pendulum.DateTime, datetime.datetime]
        :param end_time:  (Optional) The interval end time until when we want to retrieve features.
            If no timezone is specified, will default to using UTC.
        :type end_time: Union[pendulum.DateTime, datetime.datetime]
        :param save: (Optional) Whether to persist the DataFrame as a Dataset object. Default is False.
        :type save: bool
        :param save_as: (Optional) name to save the DataFrame as.
                If unspecified and save=True, a name will be generated.
        :type save_as: str

        Examples:
            A FeatureTable :py:mod:`ft` with join key :py:mod:`user_id`.

            1) :py:mod:`ft.get_historical_features(spine)` where :py:mod:`spine=pandas.Dataframe({'user_id': [1,2,3], 'date': [datetime(...), datetime(...), datetime(...)]})`
            Fetch historical features from the offline store for users 1, 2, and 3 for the specified timestamps in the spine.

            2) :py:mod:`ft.get_historical_features(spine, save_as='my_dataset)` where :py:mod:`spine=pandas.Dataframe({'user_id': [1,2,3], 'date': [datetime(...), datetime(...), datetime(...)]})`
            Fetch historical features from the offline store for users 1, 2, and 3 for the specified timestamps in the spine. Save the DataFrame as dataset with the name :py:mod`my_dataset`.

            3) :py:mod:`ft.get_historical_features(spine, timestamp_key='date_1')` where :py:mod:`spine=pandas.Dataframe({'user_id': [1,2,3], 'date_1': [datetime(...), datetime(...), datetime(...)], 'date_2': [datetime(...), datetime(...), datetime(...)]})`
            Fetch historical features from the offline store for users 1, 2, and 3 for the specified timestamps in the 'date_1' column in the spine.

            4) :py:mod:`ft.get_historical_features(start_time=datetime(...), end_time=datetime(...))`
            Fetch all historical features from the offline store in the time range specified by `start_time` and `end_time`.

        :return: A Tecton DataFrame with features values.
        """

        return self._get_historical_features(
            spine,
            timestamp_key,
            start_time,
            end_time,
            entities,
            from_source=False,
            save=save,
            save_as=save_as,
        )

    @sdk_public_method
    def get_feature_vector(
        self,
        join_keys: Optional[Mapping[str, Union[int, np.int_, str, bytes]]] = None,
        include_join_keys_in_response: bool = False,
    ) -> FeatureVector:
        """
        Deprecated.
        Returns a single Tecton FeatureVector from the Online Store.

        :param join_keys: Join keys of the enclosed FeatureTable.
        :param include_join_keys_in_response: Whether to include join keys as part of the response FeatureVector.

        :return: A FeatureVector of the results.
        """
        logger.warning(
            "Deprecated. Use the 'get_online_features' method instead to fetch features from the Online Store for this feature table. "
            + "See the api reference: https://docs.tecton.ai/api-reference/stubs/tecton.interactive.FeatureTable.html#tecton.interactive.FeatureTable.get_feature_vector"
        )
        # doing checks here instead of get_online_features in order to provide the correct error messages
        if not self._proto.feature_table.online_enabled:
            raise errors.UNSUPPORTED_OPERATION(
                "get_feature_vector", "online_serving_enabled was not defined for this Feature View."
            )
        if join_keys is None:
            raise errors.FS_GET_FEATURE_VECTOR_REQUIRED_ARGS
        return self.get_online_features(join_keys, include_join_keys_in_response)

    @sdk_public_method
    def get_online_features(
        self,
        join_keys: Mapping[str, Union[int, np.int_, str, bytes]],
        include_join_keys_in_response: bool = False,
    ) -> FeatureVector:
        """
        Returns a single Tecton FeatureVector from the Online Store.

        :param join_keys: Join keys of the enclosed FeatureTable.
        :param include_join_keys_in_response: Whether to include join keys as part of the response FeatureVector.

        Examples:
            A FeatureTable :py:mod:`ft` with join key :py:mod:`user_id`.

            1) :py:mod:`ft.get_online_features(join_keys={'user_id': 1})`
            Fetch the latest features from the online store for user 1.

            2) :py:mod:`ft.get_online_features(join_keys={'user_id': 1}, include_join_keys_in_respone=True)`
            Fetch the latest features from the online store for user 1 and include the join key information (user_id=1) in the returned FeatureVector.

        :return: A FeatureVector of the results.
        """
        if not self._proto.feature_table.online_enabled:
            raise errors.UNSUPPORTED_OPERATION(
                "get_online_features", "online_serving_enabled was not defined for this Feature Table."
            )
        validate_join_key_types(join_keys)

        return _QueryHelper(self._proto.fco_metadata.workspace, feature_view_name=self.name).get_feature_vector(
            join_keys, include_join_keys_in_response, request_context_map=None, request_context_schema=None
        )

    @sdk_public_method
    def ingest(self, df: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame]):
        """
        Ingests a Dataframe into the FeatureTable.

        :param df: The Dataframe to be ingested. Has to conform to the FeatureTable schema.
        """
        get_upload_info_request = GetNewIngestDataframeInfoRequest()
        get_upload_info_request.feature_definition_id.CopyFrom(self._id_proto)
        upload_info_response = metadata_service.instance().GetNewIngestDataframeInfo(get_upload_info_request)
        df_path = upload_info_response.df_path
        upload_url = upload_info_response.signed_url_for_df_upload

        # We write in the native format and avoid converting Pandas <-> Spark due to partially incompatible
        # type system, in specifically missing Int in Pandas
        if isinstance(df, pyspark.sql.dataframe.DataFrame):
            self._upload_df_spark(df_path, df)
        else:
            self._check_types_and_upload_df_pandas(upload_url, df_path, df)

        ingest_request = IngestDataframeRequest()
        ingest_request.workspace = self.workspace
        ingest_request.feature_definition_id.CopyFrom(self._id_proto)
        ingest_request.df_path = df_path
        response = metadata_service.instance().IngestDataframe(ingest_request)

    @sdk_public_method
    def materialization_status(self, verbose=False, limit=1000, sort_columns=None, errors_only=False):
        """
        Displays materialization information for the FeatureTable, which may include past jobs, scheduled jobs,
        and job failures.

        :param verbose: If set to true, method will display additional low level materialization information,
            useful for debugging.
        :param limit: Maximum number of jobs to return.
        :param sort_columns: A comma-separated list of column names by which to sort the rows.
        :param: errors_only: If set to true, method will only return jobs that failed with an error.
        """
        return self._materialization_status(verbose, limit, sort_columns, errors_only)

    def _check_types_and_upload_df_pandas(self, upload_url: str, df_path: str, df: pandas.DataFrame):
        tc = TectonContext.get_instance()
        spark = tc._spark
        spark_df = spark.createDataFrame(df)

        converted_schema = self._convert_ingest_schema(spark_df.schema)

        if converted_schema != spark_df.schema:
            spark_df = spark.createDataFrame(df, schema=converted_schema)

        self._upload_df_spark(df_path, spark_df)
        # Theoretically a faster way to upload native pandas DF, compared to converting to Spark DF first.
        # Currently disabled due to dependency version incompatibility between numpy==1.21.0 in DB notebooks
        # with pyarrow==0.13.0 that we pin. Can't upgrade pyarrow due to incompatibility with
        # Spark 2, see https://tecton-ai.phacility.com/D8180#141519.
        # self._upload_df_pandas(upload_url, df)

    def _convert_ingest_schema(self, ingest_schema: StructType) -> StructType:
        """
        The Pandas to Spark dataframe conversion implicitly derives the Spark schema. We handle converting/correcting
        for some type conversions where the derived schema and the feature table schema do not match.
        """
        ft_columns = self._view_schema.column_name_spark_data_types()
        ingest_columns = Schema.from_spark(ingest_schema).column_name_spark_data_types()

        converted_ingest_schema = StructType()
        int_converted_columns = []

        for col_name, col_type in ingest_columns:
            if col_type == LongType() and (col_name, IntegerType()) in ft_columns:
                int_converted_columns.append(col_name)
                converted_ingest_schema.add(col_name, IntegerType())
            elif col_type == ArrayType(DoubleType()) and (col_name, ArrayType(FloatType())) in ft_columns:
                converted_ingest_schema.add(col_name, ArrayType(FloatType()))
            else:
                converted_ingest_schema.add(col_name, col_type)

        if int_converted_columns:
            logger.warning(
                f"Tecton is casting field(s) {', '.join(int_converted_columns)} to type Integer (was type Long). To remove this warning, use a Long type in the FeatureTable schema."
            )

        return converted_ingest_schema

    def _upload_df_spark(self, df_path: str, df: pyspark.sql.dataframe.DataFrame):
        df.write.parquet(df_path)

    def _upload_df_pandas(self, upload_url: str, df: pandas.DataFrame):
        out_buffer = BytesIO()
        df.to_parquet(out_buffer, index=False)

        # Maximum 1GB per ingestion
        if out_buffer.__sizeof__() > 1000000000:
            raise errors.FT_DF_TOO_LARGE

        r = requests.put(upload_url, data=out_buffer.getvalue())
        if r.status_code != 200:
            raise errors.FT_UPLOAD_FAILED(r.reason)


@sdk_public_method
def get_feature_table(ft_reference: str, workspace_name: Optional[str] = None) -> FeatureTable:
    """
    Fetch an existing :class:`FeatureTable` by name.

    :param ft_reference: Either a name or a hexadecimal feature table ID.
    :returns: :class:`FeatureTable`
    """
    request = GetFeatureViewRequest()
    request.version_specifier = ft_reference
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().GetFeatureView(request)
    if not response.HasField("feature_view"):
        raise errors.FCO_NOT_FOUND(FeatureTable, ft_reference)

    if not response.feature_view.HasField("feature_table"):
        raise errors.FCO_NOT_FOUND_WRONG_TYPE(FeatureTable, ft_reference, "get_feature_table")

    return FeatureTable(response.feature_view)
