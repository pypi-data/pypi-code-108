"""
The dumbdbm module provides a persistent dictionary-like interface which is written entirely in Python.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.DATA_PERSISTENCE)
def open():
    """
    Open a dumbdbm database and return a dumbdbm object.
    """
    pass
