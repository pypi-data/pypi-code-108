"""
This module constructs higher-level threading interfaces on top of the lower level thread module
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


class Thread:
    """
    This class represents an activity that is run in a separate thread of control.
    """

    @tags(TagConsts.THREAD_SECURITY)
    def start(self):
        """
        Start the thread's activity.
        """
        pass
