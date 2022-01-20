"""
The multiprocessing package offers both local and remote concurrency,
effectively side-stepping the Global Interpreter Lock by using subprocesses instead of threads.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


class Process:
    """
    Process objects represent activity that is run in a separate process.
    """

    @tags(TagConsts.THREAD_SECURITY)
    def start(self):
        """
        Start the process's activity.
        """
        pass
