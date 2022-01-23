from djaws.exceptions import AWSError


class S3Error(AWSError):
    """All S3 Exceptions in the AWS App inherit from this class"""


class BucketAlreadyExists(S3Error):
    """Bucket Already Exists Error"""


class BucketAlreadyOwnedByYouError(S3Error):
    """Bucket Already Owned By You"""
