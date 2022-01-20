"""
This module performs quoted-printable transport encoding and decoding, as defined in RFC 1521
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
    """Decode the contents of the input file and write the resulting decoded binary data to the output file."""
    # parameters are dummies
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def encode(input, output):
    """Encode the contents of the input file and write the resulting quoted-printable data to the output file."""
    # parameters are dummies
    pass
