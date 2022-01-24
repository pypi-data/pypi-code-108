"""
SQLite is a C library that provides a lightweight disk-based database that doesn't
require a separate server process and allows accessing the database using a nonstandard variant of the SQL query language.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.DATA_PERSISTENCE)
def connect():
    """
    create a Connection object that represents the database
    """
    pass
