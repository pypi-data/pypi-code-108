"""
The inspect module provides several useful functions to help get information about live objects such as modules, classes, methods, functions, tracebacks, frame objects, and code objects.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.MEMORY_OBJECT_MANIPULATION)
def currentframe():
    """
    Return the frame object for the caller's stack frame.
    """
    pass


@tags(TagConsts.MEMORY_OBJECT_MANIPULATION)
def stack():
    """
    Return a list of frame records for the caller's stack.
    """
    pass


@tags(TagConsts.MEMORY_OBJECT_MANIPULATION)
def trace():
    """
    Return a list of frame records for the stack between the current frame
    and the frame in which an exception currently being handled was raised in.
    """
    pass
