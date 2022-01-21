# -*- coding: utf-8 -*-

import os
import sys
import boto3

if "CI" in os.environ:
    aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID_FOR_GITHUB_CI"]
    aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY_FOR_GITHUB_CI"]
    boto_ses = boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name="us-east-1"
    )
    runtime = "ci"
else:
    boto_ses = boto3.session.Session(profile_name="aws_data_lab_sanhe_opensource_s3pathlib")
    runtime = "local"

s3_client = boto_ses.client("s3")
bucket = "aws-data-lab-sanhe-for-opensource"
prefix = "unittest/s3pathlib/{runtime}/{os}/py{major}{minor}".format(
    runtime=runtime,
    os=sys.platform,
    major=sys.version_info.major,
    minor=sys.version_info.minor
)
