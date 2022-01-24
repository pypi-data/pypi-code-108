import pandas as pd
from views_storage import key_value_store
from views_storage import serializers
from views_storage.backends import sftp
from views_storage.backends import azure
from viewser.storage.azure import connection_string


from viewser import settings


class ForecastsStore(key_value_store.KeyValueStore):
    def __init__(self):
        super().__init__(
            backend=azure.AzureBlobStorageBackend(connection_string(
                settings.config.get("AZURE_BLOB_STORAGE_ACCOUNT_NAME"),
                settings.config.get("AZURE_BLOB_STORAGE_ACCOUNT_KEY"),
            ), "forecasts"),
            serializer=serializers.Parquet()
        )

    def write(self, name, df, run='test', overwrite=False):
        """
        Overloads the default write method to take in an additional run_id to be prepended to the file name.
        Uses whatever serializer and writer is specified in the constructor.
        :param run: Defaults to "test" if no run is given
        :param overwrite: Overwrite file if exists.
        :param name: Name of the file to write. No default if not given.
        :param df: Dataframe to write.
        :return: 0 on success.
        """
        key = f'pr_{run}_{name}.parquet'
        super().write(key, df, overwrite=overwrite)
        return 0

    def read_filename (self, file_name):
        return super().read(file_name)

    def read(self, name, run='test'):
        """
        Reads a df from the store using a key-value format
        :param name:
        :param run:
        :return:
        """
        key = f'pr_{run}_{name}.parquet'
        print(key)
        return super().read(key)


class ForecastsStore_sftp(key_value_store.KeyValueStore):
    def __init__(self):
        super().__init__(
            backend=sftp.Sftp(
                host=settings.config_get("MODEL_OBJECT_SFTP_HOSTNAME"),
                port=settings.config_get("MODEL_OBJECT_SFTP_PORT"),
                user=settings.config_get("MODEL_OBJECT_SFTP_USER"),
                key_db_host=settings.config_get("MODEL_OBJECT_KEY_DB_HOSTNAME"),
                key_db_dbname=settings.config_get("MODEL_OBJECT_KEY_DB_DBNAME"),
                folder="data/predictions"),
            serializer=serializers.Parquet()
        )

    def write(self, name, df, run='test', overwrite=False):
        """
        Overloads the default write method to take in an additional run_id to be prepended to the file name.
        Uses whatever serializer and writer is specified in the constructor.
        :param run: Defaults to "test" if no run is given
        :param overwrite: Overwrite file if exists.
        :param name: Name of the file to write. No default if not given.
        :param df: Dataframe to write.
        :return: 0 on success.
        """
        key = f'pr_{run}_{name}.parquet'
        super().write(key, df, overwrite=overwrite)
        return 0

    def read(self, name, run='test'):
        """
        Reads a df from the store using a key-value format
        :param name:
        :param run:
        :return:
        """
        key = f'pr_{run}_{name}.parquet'
        print(key)
        return super().read(key)

