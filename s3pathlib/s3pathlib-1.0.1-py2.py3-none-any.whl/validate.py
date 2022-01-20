# -*- coding: utf-8 -*-

import string

valid_bucket_charset: set = set(string.ascii_lowercase + string.digits + ".-")
letter_and_number: set = set(string.ascii_lowercase + string.digits)


def validate_s3_bucket(bucket):
    """
    Raise exception if validation not passed.

    Ref:

    - `Bucket naming rules <https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html>`_
    """
    if not (3 <= len(bucket) <= 63):
        raise ValueError("Bucket names must be between 3 and 63 characters long.")

    if len(set(bucket).difference(valid_bucket_charset)) != 0:
        raise ValueError("Bucket names can consist only of lowercase letters, numbers, dots (.), and hyphens (-).")

    if (bucket[0] not in letter_and_number) or (bucket[-1] not in letter_and_number):
        raise ValueError("Bucket names must begin and end with a letter or number.")

    # raise ValueError("Bucket names must not be formatted as an IP address (for example, 192.168.5.4).")
    # raise ValueError("Bucket names must not start with the prefix xn--.")
    # raise ValueError("Bucket names must not end with the suffix -s3alias. This suffix is reserved for access point alias names.")
    # raise ValueError("Buckets used with Amazon S3 Transfer Acceleration can't have dots (.) in their names.")


def validate_s3_key(key):
    """
    Raise exception if validation not passed.

    Ref:

    - `Key naming rules <https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html#object-key-guidelines>`_
    """
    pass


def validate_s3_uri(uri):
    pass
