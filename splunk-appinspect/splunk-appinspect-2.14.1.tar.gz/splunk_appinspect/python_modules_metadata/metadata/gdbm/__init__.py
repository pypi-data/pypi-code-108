"""
This module is quite similar to the dbm module, but uses gdbm instead to provide some additional functionality.
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
    Open a gdbm database and return a gdbm object.
    """
    pass
