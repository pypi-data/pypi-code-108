"""
The tarfile module makes it possible to read and write tar archives, including those using gzip or bz2 compression.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.DATA_COMPRESSION)
class TarFile:
    """
    Alternative constructor. The tarfile.open() function is actually a shortcut to this classmethod.
    """

    pass


@tags(TagConsts.DATA_COMPRESSION)
def open():
    """
    Return a TarFile object for the pathname name
    """
    pass
