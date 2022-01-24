"""
anydbm is a generic interface to variants of the DBM database
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.DATA_PERSISTENCE, TagConsts.PY2_ONLY)
def open():
    """
    Open the database file filename and return a corresponding object.
    """
    pass
