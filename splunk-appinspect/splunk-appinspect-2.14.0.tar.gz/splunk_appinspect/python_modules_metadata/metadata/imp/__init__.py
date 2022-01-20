"""
This module provides an interface to the mechanisms used to implement the import statement.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.MODULE_IMPORTING)
def load_module(name, file, pathname, description):
    """Load a module that was previously found by find_module() (or by an otherwise conducted search yielding
    compatible results)"""
    pass
