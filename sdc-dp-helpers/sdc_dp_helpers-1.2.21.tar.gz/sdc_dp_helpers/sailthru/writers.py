# pylint: disable=too-few-public-methods
"""
    CUSTOM WRITER CLASSES
        - Class which manages writer tasks like
        auth, write metadata, write file, create dir structure
"""
import json
import os
from datetime import datetime

import boto3


class CustomS3JsonWriter:
    """Class Extends Basic LocalGZJsonWriter"""

    def __init__(self, bucket, file_path, profile_name=None):
        self.bucket = bucket
        self.file_path = file_path

        self.profile_name = profile_name

        if profile_name is None:
            self.boto3_session = boto3.Session()
        else:
            self.boto3_session = boto3.Session(profile_name=profile_name)

        self.s3_resource = self.boto3_session.resource('s3')

    def write_to_s3(self, json_data):
        """
            Writes json data to s3 and names it by
            date of writing. Also consumes expected metadata.json file.
        """
        timestamp_suffix = datetime.now().strftime('%Y_%m_%d_%H%M%S')
        key_path = f'{os.path.join(self.file_path, timestamp_suffix)}.json'

        self.s3_resource.Object(self.bucket, key_path) \
            .put(Body=json.dumps(json_data))
