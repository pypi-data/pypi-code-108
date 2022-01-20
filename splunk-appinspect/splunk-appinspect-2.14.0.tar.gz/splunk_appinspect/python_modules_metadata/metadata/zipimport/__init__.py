"""
This module adds the ability to import Python modules (*.py, *.py[co]) and packages from ZIP-format archives.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.MODULE_IMPORTING)
class zipimporter(object):
    """Create a new zipimporter instance. archivepath must be a path to a ZIP file, or to a specific path within a
    ZIP file."""

    @tags(TagConsts.MODULE_IMPORTING)
    def load_module(self):
        """Load the module specified by fullname."""
        pass
