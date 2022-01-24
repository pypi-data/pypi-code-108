"""
manipulate config files
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.PY3_ONLY)
class RawConfigParser:
    """
    RawConfigParser class
    """

    @tags(TagConsts.FILE_READ_AND_WRITE, TagConsts.PY3_ONLY)
    def write(self):
        """
        write an .ini-format representation of the configuration state
        """
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE, TagConsts.PY3_ONLY)
    def read(self):
        """
        read and parse a filename or a list of filenames
        """
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE, TagConsts.PY3_ONLY)
    def readfp(self):
        """
        read and parse a file-like object
        """
        pass


@tags(TagConsts.PY3_ONLY)
class ConfigParser(RawConfigParser):
    """
    ConfigParser class
    """

    pass
