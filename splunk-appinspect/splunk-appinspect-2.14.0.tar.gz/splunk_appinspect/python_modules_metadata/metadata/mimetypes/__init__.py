"""
The mimetypes module converts between a filename or URL and the MIME type associated with the filename extension.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)

__tags__ = [TagConsts.INET_DATA_HANDLING]


class MimeTypes(object):
    """
    This class represents a MIME-types database.
    """

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def __init__(self, filenames=()):
        """
        The optional filenames parameter can be used to load additional files.
        """
        # parameters are dummies
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def read(self, filename):
        """Load MIME information from a file named filename."""
        # parameters are dummies
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def readfp(self, fp):
        """Load MIME type information from the Windows registry."""
        # parameters are dummies
        pass
