"""
This module builds on the asyncore infrastructure, simplifying asynchronous clients and servers and making it easier to handle protocols
whose elements are terminated by arbitrary strings, or are of variable length.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.NETWORK_CONNECTION)
class async_chat:
    """
    This class is an abstract subclass of asyncore.dispatcher.
    """

    pass
