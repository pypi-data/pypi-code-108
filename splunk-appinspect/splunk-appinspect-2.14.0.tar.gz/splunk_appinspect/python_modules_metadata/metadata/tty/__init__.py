"""
interfaces that are unique to the Unix operating system, or in some cases to some or many variants of it.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def setraw():
    """
    Change the mode of the file descriptor fd to raw
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def setcbreak():
    """
    Change the mode of file descriptor fd to cbreak
    """
    pass
