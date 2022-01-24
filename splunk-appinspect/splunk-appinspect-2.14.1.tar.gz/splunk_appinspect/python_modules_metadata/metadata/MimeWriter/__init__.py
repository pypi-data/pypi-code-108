"""
This module defines the class MimeWriter.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)

__tags__ = [TagConsts.INET_DATA_HANDLING]


class MimeWriter(object):
    """
    The MimeWriter class implements a basic formatter for creating MIME multi-part files.
    """

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def __init__(self, fp):
        """
        Return an instance of the MimeWriter class from an open file object.
        """
        # parameters are dummies
        pass
