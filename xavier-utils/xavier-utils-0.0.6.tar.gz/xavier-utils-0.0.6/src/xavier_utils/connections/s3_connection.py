from os import path
from io import BytesIO
from pandas import DataFrame
from configparser import ConfigParser
from boto3 import setup_default_session, client, resource
from pyarrow import parquet as pq

class S3_conection:
    def __init__(self, bucket_name = '/', credentials_path: str = '.aws/credentials'):
        self.credentials = self.__parsing_config(credentials_path)
        self.__create_session()
        self.client = client('s3')
        self.resource = resource('s3') 
        self.bucket_name = bucket_name

    @staticmethod
    def __parsing_config(credentials_path: str) -> dict:
        config = ConfigParser()
        _path = path.join(path.expanduser('~'), credentials_path)
        config.read(_path)
        credentials = {
                'aws_access_key_id': config.get(
                    'ilia-ecole42-xavier', 'aws_access_key_id'),
                'aws_secret_access_key': config.get(
                    'ilia-ecole42-xavier', 'aws_secret_access_key'),
                'aws_region': config.get('ilia-ecole42-xavier', 'aws_region')
                }
        return credentials

    def __create_session(self):
        setup_default_session(
                region_name=self.credentials['aws_region'],
                aws_access_key_id=self.credentials['aws_access_key_id'],
                aws_secret_access_key=self.credentials['aws_secret_access_key']
                )

    def send_to_s3(self, df: DataFrame, bucker_name: str, Key: str) -> int:
        with BytesIO() as buffer:
            df.to_parquet(buffer, index=False)
            responses = self.client.put_object(
                    Bucket=bucker_name,
                    Key=Key,
                    Body=buffer.getvalue()
                    )
        return responses.get("ResponseMetadata", {}).get("HTTPStatusCode")

    def s3_get_objects(self, bucket_name=None, prefix=''):
        if bucket_name == None:
            bucket_name = self.bucket_name
        objs = self.client.list_objects(
        Bucket=bucket_name,
        Prefix=prefix
        )
        return objs

    def get_keys(self, bucket_name=None, prefix=''):
        if bucket_name == None:
            bucket_name = self.bucket_name
        objs = self.s3_get_objects(self, bucket_name, prefix)
        return [obj['Key'] for obj in objs['Contents']]

    def get_binary_from_s3(self, bucket_name:str = None, key: str ='', to_pandas: bool = True):
        if bucket_name == None:
            bucket_name = self.bucket_name
        buffer = BytesIO()
        self.resource.Object(bucket_name, key).download_fileobj(buffer)
        if to_pandas:
            buffer = pq.read_table(buffer).to_pandas()
        return buffer

    def download_from_s3(self, bucket_name: str = None, key: str = '', path:str = '', name:str = '') -> None:
        if bucket_name == None:
            bucket_name = self.bucket_name
        self.client.download_file(
            bucket_name,
            f'{key}',
            f'{path}{name}'
            )
