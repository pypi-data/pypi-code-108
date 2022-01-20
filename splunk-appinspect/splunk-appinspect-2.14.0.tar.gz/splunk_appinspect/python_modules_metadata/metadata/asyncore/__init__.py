"""
This module provides the basic infrastructure for writing asynchronous socket service clients and servers.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.NETWORK_CONNECTION)
class dispatcher:
    """
    The dispatcher class is a thin wrapper around a low-level socket object.
    """

    pass


@tags(TagConsts.NETWORK_CONNECTION)
class dispatcher_with_send:
    """
    Adds simple buffered output capability, useful for simple clients.
    """

    pass


@tags(TagConsts.NETWORK_CONNECTION)
class file_dispatcher:
    """
    A file_dispatcher takes a file descriptor or file object along with an optional map argument and wraps it for use with the poll() or loop() functions.
    """

    pass


@tags(TagConsts.NETWORK_CONNECTION)
class file_wrapper:
    """
    A file_wrapper takes an integer file descriptor and calls os.dup() to duplicate the handle so that the original handle may be closed independently of the file_wrapper.
    """

    pass
