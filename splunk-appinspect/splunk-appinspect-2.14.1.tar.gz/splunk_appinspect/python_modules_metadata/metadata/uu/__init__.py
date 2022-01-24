"""
This module encodes and decodes files in uuencode format,
allowing arbitrary binary data to be transferred over ASCII-only connections.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)

__tags__ = [TagConsts.INET_DATA_HANDLING]


@tags(TagConsts.FILE_READ_AND_WRITE)
def decode(in_file, out_file):
    """decode Uuencoded file in_file into file out_file."""
    # parameters are dummies
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def encode(in_file, out_file):
    """encode uuencoded file in_file placing the result on file out_file."""
    # parameters are dummies
    pass
