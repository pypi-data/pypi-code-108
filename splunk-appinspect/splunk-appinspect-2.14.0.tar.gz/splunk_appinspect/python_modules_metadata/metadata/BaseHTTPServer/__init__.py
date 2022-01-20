"""
This module defines two classes for implementing HTTP servers
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.WEB_SERVER, TagConsts.PY2_ONLY)
class HTTPServer:
    """
    This class builds on the TCPServer class by storing the server address as instance variables named server_name and server_port.
    """

    pass
