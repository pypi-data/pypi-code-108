"""
This module defines classes that are useful for the manipulation for MIME multipart or encoded message.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)

__tags__ = [TagConsts.INET_DATA_HANDLING]


@tags(TagConsts.FILE_READ_AND_WRITE)
def decode(input, output, encoding):
    """Read data encoded using the allowed MIME encoding from open file object input and write the decoded data to open file object output."""
    # parameters are dummies
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def encode(input, output, encoding):
    """Read data from open file object input and write it encoded using the allowed MIME encoding to open file object output."""
    # parameters are dummies
    pass
