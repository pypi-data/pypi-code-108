"""The dbm.ndbm module provides an interface to the Unix "(n)dbm" library"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.DATA_PERSISTENCE, TagConsts.PY3_ONLY)
def open():
    """Open a dbm database and return a ndbm object"""
    pass
