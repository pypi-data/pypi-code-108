from __future__ import print_function
import asyncio
import os
import subprocess
import re
import sys
import boto3
from infinstor import infin_boto3

local_cache_data = "/local_s3_cache/data"
local_cache_metadata = "/local_s3_cache/metadata/"
PREFETCH_SCRIPT = "infin_prefetch.py"
SEP = "-_-"

def printerr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_s3_client(infinstor_time_spec):
    if infinstor_time_spec:
        return boto3.client('s3', infinstor_time_spec=infinstor_time_spec)
    else:
        return boto3.client('s3')

def download_objects(local_path, tmp_local_file, bucket, remote_path, infinstor_time_spec):
    printerr("Download from bucket {0}, path {1} to the local path {2} for timespec {3}"
             .format(bucket, remote_path, tmp_local_file, str(infinstor_time_spec)))
    asyncio.run(download_objects_async(tmp_local_file, bucket, remote_path, infinstor_time_spec))
    printerr('rename {0} to {1}'.format(tmp_local_file, local_path))
    os.rename(tmp_local_file, local_path)

async def download_one_object(local_path, bucket, remote_path, infinstor_time_spec):
    s3_client = get_s3_client(infinstor_time_spec)
    s3_client.download_file(bucket, remote_path, local_path)

async def download_objects_async(local_path, bucket, remote_path, infinstor_time_spec):
    ##download the file
    download_task = asyncio.create_task(download_one_object(local_path, bucket, remote_path,
                                                            infinstor_time_spec))
    await download_task



