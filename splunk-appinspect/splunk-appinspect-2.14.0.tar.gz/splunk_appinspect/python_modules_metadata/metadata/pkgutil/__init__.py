"""
This module provides utilities for the import system, in particular package support.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


class ImpImporter(object):
    """PEP 302 Importer that wraps Python's 'classic' import algorithm."""

    @tags(TagConsts.MODULE_IMPORTING)
    def find_module(self):
        """find_module() must return a loader object that has a single method"""
        pass


class ImpLoader(object):
    """PEP 302 Loader that wraps Python's "classic" import algorithm."""

    @tags(TagConsts.MODULE_IMPORTING)
    def load_module(self, fullname):
        """that creates and returns the corresponding module object"""
        pass
