"""
The trace module allows you to trace program execution, generate annotated statement coverage listings, print caller/callee relationships and list functions executed during a program run.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


class Trace:
    """
    Create an object to trace execution of a single statement or expression.
    """

    @tags(TagConsts.EXTERNAL_COMMAND_EXECUTION)
    def run(self):
        """Execute the command and gather statistics from the execution with the current tracing parameters."""
        pass

    @tags(TagConsts.EXTERNAL_COMMAND_EXECUTION)
    def runctx(self):
        """Execute the command and gather statistics from the execution with the current tracing parameters, in the defined global and local environments."""
        pass

    @tags(TagConsts.EXTERNAL_COMMAND_EXECUTION)
    def runfunc(self):
        """Call func with the given arguments under control of the Trace object with the current tracing parameters."""
        pass
