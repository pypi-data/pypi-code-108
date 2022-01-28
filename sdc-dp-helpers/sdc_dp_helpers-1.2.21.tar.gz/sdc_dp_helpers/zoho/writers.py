# pylint: disable=too-few-public-methods

"""
    CUSTOM WRITER CLASSES
"""
import json
from datetime import datetime

import boto3


class CustomS3JsonWriter:
    """Class Extends Basic LocalGZJsonWriter"""

    def __init__(self, bucket, profile_name=None):
        self.bucket = bucket

        self.profile_name = profile_name

        if profile_name is None:
            self.boto3_session = boto3.Session()
        else:
            self.boto3_session = boto3.Session(profile_name=profile_name)

        self.s3_resource = self.boto3_session.resource('s3')

    def write_to_s3(self, json_data, config, partition, layout='standard'):
        """
        Construct partitioning and file name conventions in s3
        according to business specifications, and write to S3.
        """
        module = config.get('module').lower()
        partial_pull = config.get('partial_pull', True)
        organisation_name = config.get('organization_name').lower()
        partial_pull_size = config.get('partial_pull_size', 5)
        now = datetime.now().strftime('%Y%m%d%H%M')

        if partial_pull:
            key_path = f'{organisation_name}/last_{partial_pull_size}_pages/{module}/{module}_{partition}_{layout}_{now}.json'
        else:
            key_path = f'{organisation_name}/full/{module}/{module}_{partition}_{layout}_full.json'

        print(f'Write path: S3://{self.bucket}/{key_path}.')

        self.s3_resource.Object(self.bucket, key_path) \
            .put(Body=json.dumps(json_data))
