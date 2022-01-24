"""
This module encodes and decodes files in binhex4 format.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)

__tags__ = [TagConsts.INET_DATA_HANDLING]


@tags(TagConsts.FILE_READ_AND_WRITE)
def binhex(input, output):
    """Convert a binary file with filename input to binhex file output."""
    # parameters are dummies
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def hexbin(input, output):
    """Decode a binhex file input."""
    # parameters are dummies
    pass
