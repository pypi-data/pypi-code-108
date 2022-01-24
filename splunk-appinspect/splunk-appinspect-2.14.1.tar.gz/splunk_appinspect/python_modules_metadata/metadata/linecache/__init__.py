"""
manipulate cache files/directories
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.FILE_READ_AND_WRITE)
def getline():
    """
    manipulate cache files/directories
    """
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def updatecache():
    """
    manipulate cache files/directories
    """
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def getlines():
    """
    manipulate cache files/directories
    """
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def clearcache():
    """
    manipulate cache files/directories
    """
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def checkcache():
    """
    manipulate cache files/directories
    """
    pass
