import logging
import os
import uuid

import boto3
from botocore.exceptions import ClientError

from djaws import decorators as aws_decorators
from djaws.s3.exceptions import S3Error, BucketAlreadyExists, BucketAlreadyOwnedByYouError
from djaws.utils import ClientErrorResponse
from djstarter import decorators, utils as core_utils

logger = logging.getLogger(__name__)


def s3_session_client(*args, **kwargs):
    session = boto3.session.Session()
    return session.client('s3', *args, **kwargs)


def create_public_access_bucket(s3_client, bucket, region=None):
    create_bucket(s3_client, bucket=bucket, region=region)
    put_public_access_block(
        s3_client,
        bucket=bucket,
        config=PublicAccessBlockConfiguration(
            block_public_acls=False,
            ignore_public_acls=False,
            block_public_policy=False,
            restrict_public_buckets=False
        )
    )
    put_bucket_cors(
        s3_client,
        bucket=bucket,
        cors_config={
            'CORSRules': [
                {
                    "AllowedHeaders": [
                        "*"
                    ],
                    "AllowedMethods": [
                        "GET"
                    ],
                    "AllowedOrigins": [
                        "*"
                    ],
                    "MaxAgeSeconds": 3000
                },
            ],
        },
    )
    return True


@aws_decorators.wrap_and_reraise_s3_errors
def create_bucket(s3_client, bucket, region=None, **kwargs):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param s3_client: S3 Client
    :param bucket: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if region is None:
            r_bucket = s3_client.create_bucket(Bucket=bucket)
        else:
            r_bucket = s3_client.create_bucket(
                Bucket=bucket,
                CreateBucketConfiguration={'LocationConstraint': region},
                **kwargs
            )
    except ClientError as e:
        raise S3ClientErrorResponse(e.response).to_s3_exception
    return CreateBucketResponse(r_bucket)


class CreateBucketResponse:
    def __init__(self, data):
        self.location = data['Location']
        # self.response_metadata = data['ResponseMetadata']


@aws_decorators.wrap_and_reraise_s3_errors
def put_bucket_cors(s3_client, bucket, cors_config):
    try:
        s3_client.put_bucket_cors(
            Bucket=bucket,
            CORSConfiguration=cors_config
        )
    except ClientError as e:
        raise S3ClientErrorResponse(e.response).to_s3_exception
    else:
        return True


@aws_decorators.wrap_and_reraise_s3_errors
def put_public_access_block(s3_client, bucket, config):
    try:
        s3_client.put_public_access_block(
            Bucket=bucket,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': config.block_public_acls,
                'IgnorePublicAcls': config.ignore_public_acls,
                'BlockPublicPolicy': config.block_public_policy,
                'RestrictPublicBuckets': config.restrict_public_buckets
            },
        )
    except ClientError as e:
        raise S3ClientErrorResponse(e.response).to_s3_exception
    else:
        return True


class PublicAccessBlockConfiguration:
    def __init__(self, block_public_acls, ignore_public_acls, block_public_policy, restrict_public_buckets):
        self.block_public_acls = block_public_acls
        self.ignore_public_acls = ignore_public_acls
        self.block_public_policy = block_public_policy
        self.restrict_public_buckets = restrict_public_buckets


@decorators.timing
@aws_decorators.wrap_and_reraise_s3_errors
def upload_object(s3_client, data, bucket, uri, key=None):
    """Upload an object to an S3 bucket

    :param key:
    :param s3_client:
    :param data: Data to upload
    :param bucket: s3 Bucket to upload to
    :param uri: Uri of object
    :return: Public S3 Url
    """

    extra_args = {
        'ContentType': core_utils.get_mimetype(uri),
        'ACL': 'public-read',
    }

    # If S3 object_name was not specified, use uuid file_name
    if key is None:
        key = f'{uuid.uuid4()}{core_utils.get_file_ext(uri)}'

    try:
        s3_client.put_object(
            Body=data,
            Bucket=bucket,
            Key=key,
            **extra_args
        )
    except ClientError as e:
        raise S3ClientErrorResponse(e.response).to_s3_exception

    return UploadFileResponse(object_name=key, bucket=bucket)


class UploadFileResponse:
    def __init__(self, object_name, bucket):
        self.object_name = object_name
        self.bucket = bucket

    @property
    def public_s3_url(self):
        return get_public_s3_url(bucket=self.bucket, key=os.path.basename(self.object_name))


@aws_decorators.wrap_and_reraise_s3_errors
def generate_presigned_post(s3_client, bucket, object_name, fields=None, conditions=None, expiration=3600):
    """Generate a presigned URL S3 POST request to upload a file

    :param s3_client:K
    :param bucket: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """
    try:
        r_presigned_url = s3_client.generate_presigned_post(
            bucket,
            object_name,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=expiration
        )
    except ClientError as e:
        raise S3ClientErrorResponse(e.response).to_s3_exception
    return PresignedPostResponse(r_presigned_url)


class PresignedPostResponse:
    def __init__(self, data):
        self.url = data['url']
        self.fields = data['fields']


class S3ClientErrorResponse(ClientErrorResponse):
    EXC_MAP = {
        'BucketAlreadyExists': BucketAlreadyExists,
        'BucketAlreadyOwnedByYou': BucketAlreadyOwnedByYouError,
    }

    @property
    def to_s3_exception(self):
        return self.EXC_MAP.get(self.exception_class, S3Error)(self.__dict__)


def get_public_s3_url(bucket, key):
    return f'https://{bucket}.s3.amazonaws.com/{key}'
