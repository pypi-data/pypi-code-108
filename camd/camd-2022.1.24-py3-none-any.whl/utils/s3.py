"""
This module consolidates generic aws s3 utilities
"""

import os

import boto3
import requests
import pandas as pd
import numpy as np
from pymatgen import Composition
from monty.os import makedirs_p
from camd import CAMD_CACHE, tqdm


def s3_sync(s3_bucket, s3_prefix, sync_path="."):
    """
    Syncs a given path to an s3 prefix

    Args:
        s3_bucket (str): bucket name
        s3_prefix (str): s3 prefix to sync to
        sync_path (str, Path): path to sync to bucket:prefix

    Returns:
        (None)

    """
    # Get bucket
    s3_resource = boto3.resource("s3")
    bucket = s3_resource.Bucket(s3_bucket)

    # Walk paths and subdirectories, uploading files
    for path, subdirs, files in os.walk(sync_path):
        # Get relative path prefix
        relpath = os.path.relpath(path, sync_path)
        if not relpath.startswith('.'):
            prefix = os.path.join(s3_prefix, relpath)
        else:
            prefix = s3_prefix

        for file in files:
            file_key = os.path.join(prefix, file)
            bucket.upload_file(os.path.join(path, file), file_key)
