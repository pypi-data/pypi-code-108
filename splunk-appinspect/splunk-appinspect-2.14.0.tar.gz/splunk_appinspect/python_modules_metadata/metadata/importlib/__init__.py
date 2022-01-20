"""This module is a minor subset of what is available in the more full-featured package of the same name from Python
3.1 that provides a complete implementation of import. What is here has been provided to help ease in transitioning
from 2.7 to 3.1. """
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.MODULE_IMPORTING)
def import_module(name, package=None):
    """Import a module."""
    pass
