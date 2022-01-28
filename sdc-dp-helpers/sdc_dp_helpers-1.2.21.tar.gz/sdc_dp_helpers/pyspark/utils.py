import gzip
import json
from urllib.parse import urlparse

import boto3
from pyspark.sql import functions as f
from pyspark.sql import types as t


def convert(field):
    """
    Handles nested json strings that need to retain their structure.
    This also guarantees that data is not lost during schema inference.
    """
    if not isinstance(field.dataType, t.StructType) and not isinstance(field.dataType, t.ArrayType):
        return field.name
    return f.to_json(field.name).alias(field.name)


def read_gz(file_url):
    """
    Reads gzipped metadata json file that has no .gz extension for spark to identify.
    """
    client = boto3.client('s3')

    url = urlparse(file_url)
    bucket, filepath = url.netloc, url.path.lstrip("/")

    obj = client.get_object(
        Bucket=bucket,
        Key=filepath
    )

    gzfile = gzip.decompress(obj['Body'].read())
    return json.loads(gzfile)


def filter_paths(bucket, prefix, position):
    """
    Gathers relevant paths in an s3 bucket and groups them by
    the specified position in the url.
    This can be used to read and write whilst retaining a specified
    level of file structuring of objects in buckets.

    Prefix can be used to speed up the search process.

    If the S3 urls are:
        s3://dl-base/metric-1/date-1
        s3://dl-base/metric-2/date-1
        s3://dl-base/metric-2/date-2
        s3://dl-base/metric-3/date-1

    One could set position to 4 and return:
        {
            'metric-1': ['s3://dl-base/metric-1/date-1'],
            'metric-2': ['s3://dl-base/metric-2/date-1', 's3://dl-base/metric-2/date-2'],
            'metric-3': ['s3://dl-base/metric-3/date-1']
        }

    """
    client = boto3.client('s3')
    paginator = client.get_paginator('list_objects')
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

    paths = []
    for page in page_iterator:
        keys = [key['Key'] for key in page['Contents']]
        for key in keys:
            key_path = f's3://{bucket}/{key}'
            if len(key_path.split('.')) > 1:
                paths.append(key_path)

    paths_dict = {}  # get all data paths associated with position
    for path in paths:
        identifier = path.split('/')[position]
        if identifier not in paths_dict:
            paths_dict[identifier] = []
        paths_dict[identifier].append(path)

    return paths_dict
