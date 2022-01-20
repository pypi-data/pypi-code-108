"""
interfaces that are unique to the Unix operating system, or in some cases to some or many variants of it.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
class Template:
    """
    An abstraction of a pipeline
    """

    @tags(TagConsts.UNIX_SPECIFIX_SERVICES)
    def open(self):
        """
        the concept of a pipeline
        """
        pass
