"""
This module provides data encoding and decoding as specified in RFC 3548.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)

__tags__ = [TagConsts.INET_DATA_HANDLING]


@tags(TagConsts.FILE_READ_AND_WRITE)
def decode(input, output):
    """Decode the contents of the input file and write the resulting binary data to the output file."""
    # parameters are dummies
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def encode(input, output):
    """Encode the contents of the input file and write the resulting base64 encoded data to the output file."""
    # parameters are dummies
    pass
