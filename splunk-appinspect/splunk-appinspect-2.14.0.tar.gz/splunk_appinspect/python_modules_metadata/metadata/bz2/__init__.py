"""
This module provides a comprehensive interface for the bz2 compression library.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.DATA_COMPRESSION)
class BZ2File:
    """
    bz2 file class
    """

    pass
