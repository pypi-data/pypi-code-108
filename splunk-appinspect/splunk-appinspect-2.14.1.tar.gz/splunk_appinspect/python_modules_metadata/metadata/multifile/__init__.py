"""
This module defines MultiFile class.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)

__tags__ = [TagConsts.INET_DATA_HANDLING]


class MultiFile(object):
    """
    The MultiFile object enables you to treat sections of a text file as file-like input objects.
    """

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def __init__(self, filenames=()):
        """
        The optional filenames parameter can be used to load additional files.
        """
        # parameters are dummies
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def readline(self):
        """Load MIME information from a file named filename."""
        # parameters are dummies
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def readlines(self):
        """Load MIME type information from the Windows registry."""
        # parameters are dummies
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def read(self):
        """Load MIME type information from the Windows registry."""
        # parameters are dummies
        pass
