"""
The SimpleXMLRPCServer module provides a basic server framework for XML-RPC servers written in Python.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.WEB_SERVER, TagConsts.PY2_ONLY)
class SimpleXMLRPCServer:
    """
    Create a new server instance. This class provides methods for registration of functions that can be called by the XML-RPC protocol.
    """

    pass
