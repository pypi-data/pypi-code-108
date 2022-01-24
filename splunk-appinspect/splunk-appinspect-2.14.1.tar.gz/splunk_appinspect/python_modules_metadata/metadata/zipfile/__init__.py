"""
This module provides tools to create, read, write, append, and list a ZIP file.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.DATA_COMPRESSION)
class ZipFile:
    """
    Open a ZIP file, where file can be either a path to a file (a string) or a file-like object.
    """

    pass
