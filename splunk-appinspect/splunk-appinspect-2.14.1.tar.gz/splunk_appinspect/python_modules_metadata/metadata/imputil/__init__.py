"""This module provides a very handy and useful mechanism for custom import hooks. Compared to the older ihooks
module, imputil takes a dramatically simpler and more straight-forward approach to custom import functions. """
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.MODULE_IMPORTING)
class Importer(object):
    """Base class for replacing standard import functions."""

    pass


@tags(TagConsts.MODULE_IMPORTING)
class BuiltinImporter(object):
    """Emulate the import mechanism for built-in and frozen modules."""

    pass


@tags(TagConsts.MODULE_IMPORTING)
def py_suffix_importer(filename, finfo, fqname):
    """Undocumented"""
    pass


@tags(TagConsts.MODULE_IMPORTING)
class DynLoadSuffixImporter(object):
    """Undocumented"""

    pass
