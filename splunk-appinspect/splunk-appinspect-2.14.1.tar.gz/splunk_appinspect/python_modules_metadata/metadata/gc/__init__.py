"""
This module provides an interface to the optional garbage collector.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.MEMORY_OBJECT_MANIPULATION)
def get_objects():
    """
    Return a list of objects tracked by the collector (excluding the list
    returned).
    """
    pass
