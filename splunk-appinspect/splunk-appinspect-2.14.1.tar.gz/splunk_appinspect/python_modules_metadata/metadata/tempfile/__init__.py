"""
manipulate temporary files/directories
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.FILE_READ_AND_WRITE)
def NamedTemporaryFile():
    """manipulate temporary files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def TemporaryFile():
    """manipulate temporary files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def mkdtemp():
    """manipulate temporary files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def mkstemp():
    """manipulate temporary files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def mktemp():
    """manipulate temporary files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def _mkstemp_inner():
    """manipulate temporary files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
class SpooledTemporaryFile:
    """manipulate temporary files/directories"""

    pass
