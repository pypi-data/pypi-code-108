# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains the descriptor of blob parquet."""

from typing import Union

from azureml._vendor.azure_storage.blob import BlockBlobService
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

from .._utils.blob_pandas_helper import read_parquet_files
from ..environ import PandasEnv, SparkEnv
from .base_blob_info import BaseBlobInfo


class BlobParquetDescriptor:
    """Defines the public data accessor.

    When you use an :mod:`azureml.opendatasets` class like :class:`azureml.opendatasets.ChicagoSafety`,
    the BlobParquetDescriptor class is used internally to access the data.
    """

    __data_name = '__data'
    __env_name = 'env'

    def __init__(self, blobInfo: BaseBlobInfo):
        """Initialize blob parquet descriptor."""
        self.__blobInfo = blobInfo

    def __get__(self, inst, cls):
        """Get inst.__data."""
        if (getattr(inst, self.__env_name, None) is None):
            print(
                "There is no data loaded until %s.env is set as SparkEnv() or PandasEnv()." % inst.__class__)
            return None

        if (getattr(inst, self.__data_name, None) is None):
            setattr(inst, self.__data_name, self._load_data(inst, inst.env))

        return getattr(inst, self.__data_name)

    def __set__(self, inst, value):
        """Set inst.__data."""
        setattr(inst, self.__data_name, value)

    def _load_data(self, inst: object, env: Union[SparkEnv, PandasEnv]):
        if isinstance(env, SparkEnv):
            return self.get_spark_dataframe(inst)
        else:
            return self.get_pandas_dataframe(inst)

    def get_spark_dataframe(self, inst):
        """
        Get a spark dataframe.

        :return: A spark dataframe based on its own filters.
        :rtype: pyspark.sql.DataFrame
        """
        container_name = self.__blobInfo.blob_container_name
        account_name = self.__blobInfo.blob_account_name
        relative_paths = self._get_target_relative_paths(inst)
        wasab_format = "wasbs://%s@%s.blob.core.windows.net/%s"
        paths = [wasab_format % (container_name, account_name, path)
                 for path in relative_paths]
        spark = SparkSession.builder.getOrCreate()

        spark.conf.set(
            'fs.azure.sas.%s.%s.blob.core.windows.net' %
            (self.__blobInfo.blob_container_name, self.__blobInfo.blob_account_name), self.__blobInfo.blob_sas_token)

        df = spark.read \
            .option("basePath", self.__blobInfo.get_data_wasbs_path()) \
            .parquet(*paths) \
            .select(inst.selected_columns)
        # in case of inst.selected_columns == ['*']
        inst.selected_columns = df.columns
        if inst.time_column_name is not None:
            return df.where((col(inst.time_column_name) >= inst.start_date) & (
                col(inst.time_column_name) <= (
                    inst.end_date if inst.end_date is not None else inst.default_end_date)))
        else:
            return df

    def get_pandas_dataframe(self, inst):
        """
        Get a pandas dataframe.

        :return: A pandas dataframe based on its own filters.
        :rtype: pandas.DataFrame
        """
        target_paths = self._get_target_relative_paths(inst)
        blob_service = BlockBlobService(
            account_name=self.__blobInfo.blob_account_name,
            sas_token=self.__blobInfo.blob_sas_token.lstrip('?'))
        if inst.cols is not None:
            all_columns = inst.selected_columns
            all_df = read_parquet_files(
                target_paths=target_paths,
                blob_container_name=self.__blobInfo.blob_container_name,
                blob_service=blob_service,
                cols=all_columns)
            if inst.time_column_name is None:
                filtered_df = all_df
            else:
                filter_mask = (all_df[inst.time_column_name] >= inst.start_date) & (
                    all_df[inst.time_column_name] <= (
                        inst.end_date if inst.end_date is not None else inst.default_end_date))
                filtered_df = all_df.loc[filter_mask]
                filtered_df = filtered_df[all_columns]
        else:
            all_df = read_parquet_files(
                target_paths=target_paths,
                blob_container_name=self.__blobInfo.blob_container_name,
                blob_service=blob_service,
                cols=None)
            if inst.time_column_name is None:
                filtered_df = all_df
            else:
                filter_mask = (all_df[inst.time_column_name] >= inst.start_date) & (
                    all_df[inst.time_column_name] <= (
                        inst.end_date if inst.end_date is not None else inst.default_end_date))
                filtered_df = all_df.loc[filter_mask]
            # in case of inst.selected_columns == ['*']
            inst.selected_columns = list(filtered_df.columns)

        print('Done.')
        return filtered_df

    def _get_target_relative_paths(self, inst):
        """
        Get relative path of blob files.

        :return: list of relative files.
        :rtype: List[str]
        """
        success, blob_account_name, blob_container_name, blob_relative_path, blob_sas_token = \
            self.__blobInfo.get_blob_metadata()
        if success:
            self.__blobInfo.blob_account_name = blob_account_name
            self.__blobInfo.blob_container_name = blob_container_name
            self.__blobInfo.blob_relative_path = blob_relative_path
            self.__blobInfo.blob_sas_token = blob_sas_token

        blob_service = BlockBlobService(
            account_name=self.__blobInfo.blob_account_name,
            sas_token=self.__blobInfo.blob_sas_token.lstrip('?'))
        target_paths = inst.get_pandas_limit().get_target_blob_paths(
            blob_service=blob_service,
            blob_container_name=self.__blobInfo.blob_container_name,
            blob_relative_path=self.__blobInfo.blob_relative_path)

        if not target_paths:
            raise ValueError(
                'Cannot find target blob paths for given input datetime range:\n\tstart date: %s\n\tend date: %s' % (
                    inst.start_date, inst.end_date if inst.end_date is not None else inst.end_date))

        return target_paths
