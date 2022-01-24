"""
This module provides a ModuleFinder class that can be used to determine the set of modules imported by a script.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.MODULE_IMPORTING)
def ReplacePackage(oldname, newname):
    """Allows specifying that the module named oldname is in fact the package named newname"""
    pass


class ModuleFinder(object):
    """This class provides run_script() and report() methods to determine the set of modules imported by a script."""

    @tags(TagConsts.MODULE_IMPORTING)
    def run_script(self, pathname):
        """Analyze the contents of the pathname file, which must contain Python code."""
        pass
