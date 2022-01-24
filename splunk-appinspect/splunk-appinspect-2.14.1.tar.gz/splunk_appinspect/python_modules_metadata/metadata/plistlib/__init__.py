"""
manipulate .plist files in MacOS
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.FILE_READ_AND_WRITE)
def writePlist():
    """
    write rootObject to a .plist file
    """
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def writePlistToResource():
    """
    write rootObject to a .plist file
    """
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def readPlist():
    """
    read a .plist file
    """
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def readPlistFromResource():
    """
    read plst resource from the resource fork of path
    """
    pass
