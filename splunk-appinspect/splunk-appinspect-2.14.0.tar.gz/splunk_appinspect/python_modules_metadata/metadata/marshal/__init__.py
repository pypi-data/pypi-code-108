"""
This module contains functions that can read and write Python values in a binary format.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.DATA_PERSISTENCE)
def load():
    """
    Read one value from the open file and return it
    """
    pass


@tags(TagConsts.DATA_PERSISTENCE)
def dump():
    """
    Write the value on the open file.
    """
    pass
