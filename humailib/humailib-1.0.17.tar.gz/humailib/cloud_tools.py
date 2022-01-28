import os
import re
import shutil
import dill as pickle
import json
import sys
from pathlib import Path
import warnings

from google.cloud import storage
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import google.oauth2
import pandas_gbq

# https://docs.microsoft.com/en-us/python/api/overview/azure/storage-file-datalake-readme?view=azure-python
from azure.storage.filedatalake import DataLakeFileClient
from azure.storage.blob import BlobServiceClient

import pandas as pd


class GoogleBigQuery:
    
    def __init__(
        self, 
        project, 
        key,
        cache_dir='./cache'
    ):
        self.key = key
        self.credentials = google.oauth2.service_account.Credentials.from_service_account_file(self.key)
        self.gbq = bigquery.Client.from_service_account_json(self.key)
        self.project = project
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        return

    def _table_to_filename(self, dataset_table):

        return dataset_table.replace('.','_') + '.csv'
    
    def table_exists(self, dataset_table):
    
        try:
            self.gbq.get_table(dataset_table)
            return True
        except NotFound:
            return False

    def download_table_to_pandas(
        self, 
        dataset_table, 
        sql=None, 
        datetime_columns=None, 
        datetime_format='%Y-%m-%d %H:%M:%S', 
        deduplicate=True, 
        flush_cache=False,
        use_pandas_gbq=True
    ):

        cache_file = Path(self.cache_dir + '/' + self._table_to_filename(dataset_table))
        if not flush_cache and cache_file.is_file():
            print("[download_table_to_pandas] Retrieving from cache: {}...".format(cache_file))
            df = pd.read_csv(cache_file)
            
            if datetime_columns is not None:
                for dtc in datetime_columns:
                    df.loc[:,dtc] = pd.to_datetime(df[dtc], format=datetime_format, utc=True).dt.tz_convert(None)
        else:
            if sql is None:
                if deduplicate:
                    sql = """
                    SELECT DISTINCT
                    * 
                    FROM 
                    `{0}`
                    """.format(dataset_table)
                else:
                    sql = """
                    SELECT
                    * 
                    FROM 
                    `{0}`
                    """.format(dataset_table)
            
            if not self.table_exists(dataset_table):
                print("[download_table_to_pandas] Project '{}': Table {} does not exist!".format(self.project, dataset_table))
                return None
            
            print("[download_table_to_pandas] Project '{}': Retrieving {} using query {}...".format(self.project, dataset_table, sql))
            if use_pandas_gbq:
                df = pandas_gbq.read_gbq(
                    sql,
                    #progress_bar_type = 'tqdm',
                    dialect='standard',
                    use_bqstorage_api=True,
                    project_id = self.project,
                    credentials = self.credentials
                )
            else:
                df = self.gbq.query(sql).to_dataframe()

            print("[download_table_to_pandas] Writing {} to cache {}...".format(dataset_table, cache_file))
            df.reset_index(drop=True).to_csv(cache_file, index=False)

            if datetime_columns is not None:
                for dtc in datetime_columns:
                    df.loc[:,dtc] = pd.to_datetime(df[dtc], format=datetime_format, utc=True).dt.tz_convert(None)

        print("[download_table_to_pandas] Retrieved {:,} rows".format(len(df)))

        return df
        
    def upload_table(
        self,
        df,
        dataset_table,
        if_exists = 'append'
    ):
        cache_file = Path(self.cache_dir + '/' + self._table_to_filename(dataset_table))

        print("[upload_table] Updating cache for {}...".format(dataset_table))
        df.reset_index(drop=True).to_csv(cache_file, index=False)
        #df.to_csv(cache_file, index=False)

        print("[upload_table] Project '{}': Uploading {:,} rows to BQ using rule '{}': {}...".format(self.project, len(df), if_exists, dataset_table))

        pandas_gbq.to_gbq(
            df,
            destination_table = dataset_table,
            project_id = self.project,
            #progress_bar_type = 'tqdm',
            if_exists = if_exists,
            location = 'EU',
            credentials = self.credentials
        )
        
    def upload_and_replace_table(
        self, 
        df, dataset_table
    ):
        return self.upload_table(df, dataset_table, if_exists='replace')


def loadDatasetToPandas(dataset, from_cloud=False, delimiter=',', convertDatetime=True, datetime_format='%Y-%m-%dT%H:%M:%S.000Z', 
    key='../../service_account_keys/humai-sb-7b9db70de787.json'):
    warnings.warn('please use humailib.cloud_tools.GoogleBigQuery.download_table_to_pandas(...)', category=DeprecationWarning, stacklevel=1)
    return


def uploadDataframeToBQ(dataframe, dataset_name, project='humai-sb', key='../../service_account_keys/humai-sb-7b9db70de787.json'):
    warnings.warn('please use humailib.cloud_tools.GoogleBigQuery.upload_and_replace_table(...)', category=DeprecationWarning, stacklevel=1)
    return

    
# Copyright 2017, Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# This code has been modified slightly by William H. de Boer
# 27/03/2019.

"""Helpers for accessing Google Cloud Storage in Python code.
`pickle_and_upload`: Upload a Python object after pickling to
user-specified `bucket_name` and `object_name`.
`download_and_unpickle`: The opposite of `pickle_and_upload`.
For more information:
https://cloud.google.com/storage/
"""

class GoogleCloudStorage:
    
    def __init__(self, key, cache_dir='./cache'):
        self.storage_client = storage.Client.from_service_account_json(key)
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            print("Created cache directory '{}'".format(self.cache_dir))

        return
   
    def _make_gcs_uri(self, bucket_name, object_name):
        return 'gs://{}/{}'.format(bucket_name, object_name)

    def _split_uri(self, gcs_uri):
        """Splits gs://bucket_name/object_name to (bucket_name, object_name)"""
        pattern = r'gs://([^/]+)/(.+)'
        match = re.match(pattern, gcs_uri)

        bucket_name = match.group(1)
        object_name = match.group(2)

        return bucket_name, object_name
    
    def _get_cache_file(self, filename):
        
        return self.cache_dir + '/' + filename.split('://')[-1].replace('/','_').replace('-','_')

    def get_blob(self, bucket_name, object_name):
    
        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(object_name)
        return blob

    def get_uri_blob(self, gcs_uri):
        bucket_name, object_name = self._split_uri(gcs_uri)
        return self.get_blob(bucket_name, object_name)

    def list_blobs(self, bucket_name, directory=None):

        if directory is None or len(directory) == 0:
            directory = None
            n = 0
        else:
            add = 0 if directory[-1] == '/' else 1
            n = len(directory) + add # added 1 for the '/'
        
        bucket = self.storage_client.get_bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=directory)

        blobs = [blob.name[n:] or '.' for blob in blobs]

        return blobs
    
    def file_exists(self, bucket_name, filepath):
        
        ret = self.list_blobs(bucket_name, directory=filepath)
        if len(ret) == 0:
            return False
        
        return ret[0] == '.'

    def upload_file(self, source_filename, dest_filename):
        """Archives a directory and upload to GCS.
        Returns the object's GCS uri.
        """

        bucket_name, object_name = self._split_uri(dest_filename)
        #print(bucket_name, object_name)
        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(object_name)
        #print(source_filename)
        blob.upload_from_filename(source_filename)

        print('[upload_file] Uploaded {0} to {1}'.format(source_filename, self._make_gcs_uri(bucket_name, object_name)))

        return self._make_gcs_uri(bucket_name, object_name)

    def download_file(self, source_filename, dest_filename):

        bucket_name, object_name = self._split_uri(source_filename)
        blob = self.get_blob(bucket_name, object_name)
        #print(bucket_name, object_name, dest_filename)
        with open(str(dest_filename), "wb") as file_obj:
            ret = blob.download_to_file(file_obj)

        print("[download_file] Downloading {0} to {1}".format(self._make_gcs_uri(bucket_name, object_name), dest_filename))

        return ret

    def upload_csv(
        self, 
        df,
        dest_filename,
        **kwargs,
    ):

        cache_file = self._get_cache_file(dest_filename)
        print("[upload_csv] Writing to cache: {}...".format(cache_file))
        df.reset_index(drop=True).to_csv(cache_file, index=False, **kwargs)
        #df.to_csv(cache_file, index=False)

        print("[upload_csv] Uploading dataframe ({:,} rows) to {}...".format(len(df), dest_filename))
        self.upload_file(cache_file, dest_filename)

        return
    
    def upload_excel(
        self, 
        df,
        dest_filename):

        cache_file = self._get_cache_file(dest_filename)
        print("[upload_excel] Writing to cache: {}...".format(cache_file))
        df.reset_index(drop=True).to_excel(cache_file, index=False)
        #df.to_csv(cache_file, index=False)

        print("[upload_excel] Uploading dataframe ({:,} rows) to {}...".format(len(df), dest_filename))
        self.upload_file(cache_file, dest_filename)

        return
    
    def upload_json(self, data, dest_filename):
        
        cache_file = self._get_cache_file(dest_filename)
        print("[upload_json] Writing to cache: {}...".format(cache_file))
        with open(cache_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        print("[upload_json] Uploading to {}...".format(dest_filename))
        self.upload_file(cache_file, dest_filename)
        
        return
        
    def download_csv(
        self, 
        source_filename, 
        datetime_columns=None, datetime_format='%Y-%m-%d %H:%M:%S', 
        flush_cache=True,
        **kwargs,
    ):

        cache_file = Path(self._get_cache_file(source_filename))
        if not flush_cache and cache_file.is_file():
            print("[download_csv] Retrieving from cache: {}...".format(cache_file))
        else:
            print("[download_csv] Downloading and caching: {}...".format(source_filename))
            self.download_file(source_filename, cache_file)    

        df = pd.read_csv(cache_file, **kwargs)
        
        if datetime_columns is not None:
            for dtc in datetime_columns:
                df.loc[:,dtc] = pd.to_datetime(df[dtc], format=datetime_format, utc=True).dt.tz_convert(None)
                
        print("[download_csv] Read {:,} rows".format(len(df)))

        return df

    def download_excel(
        self, 
        source_filename, 
        flush_cache=True,
        **kwargs,
    ):

        cache_file = Path(self._get_cache_file(source_filename))
        if not flush_cache and cache_file.is_file():
            print("[download_excel] Retrieving from cache: {}...".format(cache_file))
        else:
            print("[download_excel] Downloading and caching: {}...".format(source_filename))
            self.download_file(source_filename, cache_file)    
            
        """ if use_cache:
            if cache_file.is_file():
                print("[download_excel] Retrieving from cache: {}...".format(cache_file))
            else:
                print("[download_excel] Downloading and caching {}...".format(source_filename))
                self.download_file(source_filename, cache_file)
        else:
            print("[download_excel] Downloading and re-caching {}...".format(source_filename))
            self.download_file(source_filename, cache_file)"""

        df = pd.read_excel(cache_file, engine='openpyxl', **kwargs)

        print("[download_excel] Read {:,} rows".format(len(df)))

        return df
    
    def download_json(
        self, 
        source_filename, 
        flush_cache=True,
        **kwargs,
    ):

        cache_file = Path(self._get_cache_file(source_filename))
        if not flush_cache and cache_file.is_file():
            print("[download_json] Retrieving from cache: {}...".format(cache_file))
        else:
            print("[download_json] Downloading and caching: {}...".format(source_filename))
            self.download_file(source_filename, cache_file)    

        with cache_file.open(mode='r') as json_file:
            data = json.load(json_file, **kwargs)

        return data


    def pickle_and_upload(self, obj, dest_filename):
        """Returns the object's GCS uri."""
        print('Pickling data')
        pickle_str = pickle.dumps(obj)
        
        bucket_name, object_name = self._split_uri(dest_filename)
        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(object_name)
        print('Uploading to {}...'.format(dest_filename))
        blob.upload_from_string(pickle_str)

        return self._make_gcs_uri(bucket_name, object_name)

    def download_and_unpickle(self, source_filename):
        
        bucket_name, object_name = self._split_uri(source_filename)
        blob = self.get_blob(bucket_name, object_name)
        pickle_str = blob.download_as_string()

        print('Downloading and unpickling {}...'.format(source_filename))
        obj = pickle.loads(pickle_str)
        return obj

    def download_uri_and_unpickle(self, gcs_uri):
        bucket_name, object_name = self._split_uri(gcs_uri)
        obj = self.download_and_unpickle(bucket_name, object_name)

        return obj

    def archive_and_upload(self, bucket_name, directory, extension='zip', object_name=None):
        """Archives a directory and upload to GCS.
        Returns the object's GCS uri.
        """
        object_name = object_name or '{}.{}'.format(directory, extension)

        temp_filename = shutil.make_archive('_tmp', extension, directory)

        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(object_name)
        blob.upload_from_filename(temp_filename)

        os.remove(temp_filename)

        return self._make_gcs_uri(bucket_name, object_name)



class AzureDataLake:
    
    def __init__(
        self, 
        project, 
        key,
        cache_dir='./cache'
    ):
        self.key = key
        
        self.project = project
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        return

    def _table_to_cache_filename(self, dataset_table):

        return dataset_table.replace('.','_').replace(' ','_') + '.parq'

    def _table_to_adls_filename(self, dataset_table):

        return dataset_table.replace('.','/').replace(' ','_') + '.parq'
    
    def table_exists(self, dataset_table):
    
        input_path = self._table_to_adls_filename(dataset_table)
        print(input_path)
        azure_file = DataLakeFileClient.from_connection_string(
            self.key,
            file_system_name=self.project, file_path=input_path
        )
        return azure_file.exists()

    def download_table_to_pandas(
        self, 
        dataset_table, 
        #sql=None, 
        datetime_columns=None, 
        datetime_format='%Y-%m-%d %H:%M:%S', 
        deduplicate=True, 
        flush_cache=False,
    ):
        input_path = self._table_to_adls_filename(dataset_table)
        cache_file = Path(self.cache_dir + '/' + self._table_to_cache_filename(dataset_table))
        if not flush_cache and cache_file.is_file() and not deduplicate:
            print("[download_table_to_pandas] Retrieving from cache: {}...".format(cache_file))
            df = pd.read_parquet(cache_file)
            
            if datetime_columns is not None:
                for dtc in datetime_columns:
                    if dtc in df:
                        df.loc[:,dtc] = pd.to_datetime(df[dtc], format=datetime_format, utc=True).dt.tz_convert(None)
        else:

            azure_file = DataLakeFileClient.from_connection_string(
                self.key,
                file_system_name=self.project, file_path=input_path
            )

            if not self.table_exists(dataset_table):
                print("[download_table_to_pandas] Project '{}': Table {} does not exist!".format(self.project, dataset_table))
                return None

            print("[download_table_to_pandas] Writing {} to cache {}...".format(dataset_table, cache_file))
            with open(cache_file, "wb") as tmp_file:
                download = azure_file.download_file()
                download.readinto(tmp_file)
            
            df = pd.read_parquet(cache_file)
            if deduplicate:
                print("  dropping duplicates...")
                df = df.drop_duplicates()
            
            if datetime_columns is not None:
                for dtc in datetime_columns:
                    if dtc in df:
                        df.loc[:,dtc] = pd.to_datetime(df[dtc], format=datetime_format, utc=True).dt.tz_convert(None)

        print("[download_table_to_pandas] Retrieved {:,} rows".format(len(df)))

        return df
        
    def upload_table(
        self,
        df,
        dataset_table,
        if_exists = 'append'
    ):
        output_path = self._table_to_adls_filename(dataset_table)
        cache_file = Path(self.cache_dir + '/' + self._table_to_cache_filename(dataset_table))

        if if_exists == 'append':
            df_in = self.download_table_to_pandas(dataset_table, deduplicate=False, flush_cache=True)
            df = df.append(df_in, ignore_index=True)

        print("[upload_table] Updating cache for {}...".format(dataset_table))
        df.reset_index(drop=True).to_parquet(cache_file, index=False, allow_truncated_timestamps=True)
        azure_file = DataLakeFileClient.from_connection_string(
            self.key,
            file_system_name=self.project, file_path=output_path
        )

        print("[upload_table] Project '{}': Uploading {:,} rows to ADLS Gen2 using rule '{}': {}...".format(self.project, len(df), if_exists, output_path))
        azure_file.create_file()
        with open(cache_file, "rb") as data:
            azure_file.upload_data(data, overwrite=True)

        print("[upload_table] Done.")
        
    def upload_and_replace_table(
        self, 
        df, dataset_table
    ):
        return self.upload_table(df, dataset_table, if_exists='replace')



class AzureBlobStorage:
    
    def __init__(self, key, cache_dir='./cache'):
        self.storage_client = BlobServiceClient.from_connection_string(connection_string)
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            print("Created cache directory '{}'".format(self.cache_dir))

        return
   
    def _make_gcs_uri(self, bucket_name, object_name):
        return '{}/{}'.format(bucket_name, object_name)

    def _split_uri(self, gcs_uri):
        """Splits bucket_name/object_name to (bucket_name, object_name)"""
        pattern = r'([^/]+)/(.+)'
        match = re.match(pattern, gcs_uri.split('://')[-1])

        bucket_name = match.group(1)
        object_name = match.group(2)

        return bucket_name, object_name
    
    def _get_cache_file(self, filename):
        
        return self.cache_dir + '/' + filename.split('://')[-1].replace('/','_').replace('-','_')

    def get_blob(self, bucket_name, object_name):

        bucket_name = bucket_name.split('://')[-1]
    
        blob_client = self.storage_client.get_blob_client(container=bucket_name, blob=object_name)
        return blob_client.download_blob().readall()

    def get_uri_blob(self, uri):
        bucket_name, object_name = self._split_uri(uri)
        return self.get_blob(bucket_name, object_name)

    def list_blobs(self, bucket_name):

        bucket_name = bucket_name.split('://')[-1]
        container_client = self.storage_client.get_container_client(bucket_name)
        blobs = container_client.list_blobs()

        return [blob.name for blob in blobs]
    
    def file_exists(self, bucket_name, filepath):
        
        bucket_name = bucket_name.split('://')[-1]
        blob_client = self.storage_client.get_blob_client(container=bucket_name, blob=filepath)

        return blob_client.exists()

    def upload_file(self, source_filename, dest_filename, overwrite=True):
        """Archives a directory and upload to GCS.
        Returns the object's GCS uri.
        """

        bucket_name, object_name = self._split_uri(dest_filename)
        #print(bucket_name, object_name)
        blob_client = self.storage_client.get_blob_client(container=bucket_name, blob=object_name)
        
        with open(source_filename, "rb") as upload_file:
            blob_client.upload_blob(upload_file, blob_type="BlockBlob", overwrite=overwrite)

        print('[upload_file] Uploaded {0} to {1}'.format(source_filename, self._make_gcs_uri(bucket_name, object_name)))

        return self._make_gcs_uri(bucket_name, object_name)

    def download_file(self, source_filename, dest_filename):

        bucket_name, object_name = self._split_uri(source_filename)
        blob_client = self.storage_client.get_blob_client(container=bucket_name, blob=object_name)

        with open(dest_filename, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        print("[download_file] Downloading {0} to {1}".format(self._make_gcs_uri(bucket_name, object_name), dest_filename))

        return True

    def upload_csv(
        self, 
        df,
        dest_filename,
        **kwargs,
    ):

        cache_file = self._get_cache_file(dest_filename)
        print("[upload_csv] Writing to cache: {}...".format(cache_file))
        df.reset_index(drop=True).to_csv(cache_file, index=False, **kwargs)
        #df.to_csv(cache_file, index=False)

        print("[upload_csv] Uploading dataframe ({:,} rows) to {}...".format(len(df), dest_filename))
        self.upload_file(cache_file, dest_filename)

        return
    
    def upload_excel(
        self, 
        df,
        dest_filename):

        cache_file = self._get_cache_file(dest_filename)
        print("[upload_excel] Writing to cache: {}...".format(cache_file))
        df.reset_index(drop=True).to_excel(cache_file, index=False)
        #df.to_csv(cache_file, index=False)

        print("[upload_excel] Uploading dataframe ({:,} rows) to {}...".format(len(df), dest_filename))
        self.upload_file(cache_file, dest_filename)

        return
    
    def upload_json(self, data, dest_filename):
        
        cache_file = self._get_cache_file(dest_filename)
        print("[upload_json] Writing to cache: {}...".format(cache_file))
        with open(cache_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        print("[upload_json] Uploading to {}...".format(dest_filename))
        self.upload_file(cache_file, dest_filename)
        
        return
        
    def download_csv(
        self, 
        source_filename, 
        datetime_columns=None, datetime_format='%Y-%m-%d %H:%M:%S', 
        flush_cache=True,
        **kwargs,
    ):

        cache_file = Path(self._get_cache_file(source_filename))
        if not flush_cache and cache_file.is_file():
            print("[download_csv] Retrieving from cache: {}...".format(cache_file))
        else:
            print("[download_csv] Downloading and caching: {}...".format(source_filename))
            self.download_file(source_filename, cache_file)    

        df = pd.read_csv(cache_file, **kwargs)
        
        if datetime_columns is not None:
            for dtc in datetime_columns:
                df.loc[:,dtc] = pd.to_datetime(df[dtc], format=datetime_format, utc=True).dt.tz_convert(None)
                
        print("[download_csv] Read {:,} rows".format(len(df)))

        return df

    def download_excel(
        self, 
        source_filename, 
        flush_cache=True,
        **kwargs,
    ):

        cache_file = Path(self._get_cache_file(source_filename))
        if not flush_cache and cache_file.is_file():
            print("[download_excel] Retrieving from cache: {}...".format(cache_file))
        else:
            print("[download_excel] Downloading and caching: {}...".format(source_filename))
            self.download_file(source_filename, cache_file)    
            
        """ if use_cache:
            if cache_file.is_file():
                print("[download_excel] Retrieving from cache: {}...".format(cache_file))
            else:
                print("[download_excel] Downloading and caching {}...".format(source_filename))
                self.download_file(source_filename, cache_file)
        else:
            print("[download_excel] Downloading and re-caching {}...".format(source_filename))
            self.download_file(source_filename, cache_file)"""

        df = pd.read_excel(cache_file, engine='openpyxl', **kwargs)

        print("[download_excel] Read {:,} rows".format(len(df)))

        return df
    
    def download_json(
        self, 
        source_filename, 
        flush_cache=True,
        **kwargs,
    ):

        cache_file = Path(self._get_cache_file(source_filename))
        if not flush_cache and cache_file.is_file():
            print("[download_json] Retrieving from cache: {}...".format(cache_file))
        else:
            print("[download_json] Downloading and caching: {}...".format(source_filename))
            self.download_file(source_filename, cache_file)    

        with cache_file.open(mode='r') as json_file:
            data = json.load(json_file, **kwargs)

        return data


    def pickle_and_upload(self, obj, dest_filename):
        """Returns the object's GCS uri."""
        print('Pickling data')
        pickle_str = pickle.dumps(obj)
        
        bucket_name, object_name = self._split_uri(dest_filename)
        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(object_name)
        print('Uploading to {}...'.format(dest_filename))
        blob.upload_from_string(pickle_str)

        return self._make_gcs_uri(bucket_name, object_name)

    def download_and_unpickle(self, source_filename):
        
        bucket_name, object_name = self._split_uri(source_filename)
        blob = self.get_blob(bucket_name, object_name)
        pickle_str = blob.download_as_string()

        print('Downloading and unpickling {}...'.format(source_filename))
        obj = pickle.loads(pickle_str)
        return obj

    def download_uri_and_unpickle(self, gcs_uri):
        bucket_name, object_name = self._split_uri(gcs_uri)
        obj = self.download_and_unpickle(bucket_name, object_name)

        return obj

    def archive_and_upload(self, bucket_name, directory, extension='zip', object_name=None):
        """Archives a directory and upload to GCS.
        Returns the object's GCS uri.
        """
        object_name = object_name or '{}.{}'.format(directory, extension)

        temp_filename = shutil.make_archive('_tmp', extension, directory)

        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(object_name)
        blob.upload_from_filename(temp_filename)

        os.remove(temp_filename)

        return self._make_gcs_uri(bucket_name, object_name)


       
