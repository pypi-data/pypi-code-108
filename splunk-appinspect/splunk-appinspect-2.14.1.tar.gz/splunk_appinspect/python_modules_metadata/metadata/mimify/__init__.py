"""
The mimify module defines functions to convert mail messages to and from MIME format.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)

__tags__ = [TagConsts.INET_DATA_HANDLING]


@tags(TagConsts.FILE_READ_AND_WRITE)
def mimify(infile, outfile):
    """Copy the message in infile to outfile."""
    # parameters are dummies
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def unmimify(input, output, encoding):
    """Copy the message in infile to outfile, decoding all quoted-printable parts."""
    # parameters are dummies
    pass
