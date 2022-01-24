"""
The code module provides facilities to implement read-eval-print loops in Python.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


class InteractiveInterpreter(object):
    """
    This class deals with parsing and interpreter state
    """

    @tags(TagConsts.STRING_EXECUTION)
    def runsource(self):
        """
        Compile and run some source in the interpreter.
        """
        pass

    @tags(TagConsts.STRING_EXECUTION)
    def runcode(self):
        """
        Execute a code object.
        """
        pass


class InteractiveConsole(object):
    """
    Closely emulate the behavior of the interactive Python interpreter.
    """

    @tags(TagConsts.STRING_EXECUTION)
    def push(self):
        """
        Push a line of source text to the interpreter.
        """
        pass
