import logging
from typing import Tuple

import boto3 as boto3
import redshift_connector
from boto3 import Session
from botocore.exceptions import ClientError


class AWSUtil:
    logger = logging.getLogger(__name__)

    def __init__(self,
                 redshift_host: str,
                 redshift_port: int,
                 redshift_database: str,
                 redshift_user: str,
                 redshift_password: str,
                 s3_bucket: str):
        # Use the credential policy from boto3 to get access key and secret key
        session = Session()
        credentials = session.get_credentials()
        current_credentials = credentials.get_frozen_credentials()

        self.access_key_id = current_credentials.access_key
        self.secret_access_key = current_credentials.secret_key
        self.redshift_host = redshift_host
        self.redshift_port = redshift_port
        self.redshift_database = redshift_database
        self.redshift_user = redshift_user
        self.redshift_password = redshift_password
        self.s3_bucket = s3_bucket

    @staticmethod
    def get_resource_s3_path(resource_name: str, started_at: int) -> (str, str):
        return f'redshift/{resource_name}/{resource_name}_{started_at}.csv'

    def copy_to_s3(self, output_path: str, bucket: str, obj_name: str):
        s3_client = boto3.client('s3')
        try:
            s3_client.upload_file(output_path, bucket, obj_name)
        except ClientError as e:
            self.logger.error(e)

        self.logger.debug(f'Copy {output_path} to s3, bucket: {bucket}, object name: {obj_name}')

    def rm_s3(self, bucket: str, obj_name: str):
        s3 = boto3.resource('s3')
        s3.Object(bucket, obj_name).delete()

        self.logger.debug(f'Remove a s3 file, bucket: {bucket}, object name: {obj_name}')

    def copy_to_redshift(self,
                         redshift_table_name: str,
                         resource_s3_path: str):

        self.exec_query_commit(f"copy {redshift_table_name} "
                               f"from '{resource_s3_path}' "
                               f"access_key_id '{self.access_key_id}' "
                               f"secret_access_key '{self.secret_access_key}' "
                               f"timeformat 'epochsecs' "
                               f"csv IGNOREHEADER 1;")

        self.logger.debug(f'Copy a {resource_s3_path} to redshift, table: {redshift_table_name}')

    def exec_query_get_result(self, query: str) -> Tuple:

        with redshift_connector.connect(
                host=self.redshift_host,
                port=self.redshift_port,
                database=self.redshift_database,
                user=self.redshift_user,
                password=self.redshift_password
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)

            return cursor.fetchall()

    def exec_query_commit(self, query: str):

        with redshift_connector.connect(
                host=self.redshift_host,
                port=self.redshift_port,
                database=self.redshift_database,
                user=self.redshift_user,
                password=self.redshift_password
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)

            conn.commit()
