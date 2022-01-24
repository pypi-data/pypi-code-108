"""The dbm.gnu module provides an interface to the GNU DBM library"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.DATA_PERSISTENCE, TagConsts.PY3_ONLY)
def open():
    """Open a gdbm database and return a gdbm object"""
    pass
