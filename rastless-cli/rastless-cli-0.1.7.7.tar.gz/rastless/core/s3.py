import boto3
import os
from typing import List

from rastless.db.models import LayerStepModel


class S3Bucket:
    def __init__(self, bucket_name, region="eu-central-1"):
        self.bucket_name = bucket_name
        self.s3 = boto3.resource('s3', region_name=region)
        self.s3_client = boto3.client('s3')
        self.bucket = self.s3.Bucket(bucket_name)

    def delete_object(self, object_name):
        self.s3.Object(self.bucket_name, object_name).delete()

    def list_bucket_entries(self, prefix=None):
        bucket = self.s3.Bucket(self.bucket_name)
        if prefix:
            files = bucket.objects.filter(Prefix=prefix)
        else:
            files = bucket.objects.all()

        return list(files)

    def delete_layer_steps(self, layer_steps: List[LayerStepModel]):
        for step in layer_steps:
            self.delete_object(step.s3_object_name(self.bucket_name))


