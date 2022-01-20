"""
pickle module implements a fundamental, but powerful algorithm for serializing and de-serializing a Python object structure.
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
    Read a string from the open file object file and interpret it as a pickle data stream, reconstructing and returning the original object hierarchy.
    """
    pass


@tags(TagConsts.DATA_PERSISTENCE)
def dump():
    """
    Write a pickled representation of obj to the open file object file.
    """
    pass
