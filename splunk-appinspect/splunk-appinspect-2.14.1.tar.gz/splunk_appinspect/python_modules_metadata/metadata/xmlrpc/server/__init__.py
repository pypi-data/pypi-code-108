"""This module supports writing XML-RPC server code"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.WEB_SERVER, TagConsts.PY3_ONLY)
class SimpleXMLRPCServer(object):
    """This class provides methods for registration of functions that can be called by the XML-RPC protocol"""

    pass


@tags(TagConsts.WEB_SERVER, TagConsts.PY3_ONLY)
class DocXMLRPCServer(object):
    """These classes extend the above classes to serve HTML documentation in response to HTTP GET requests"""

    pass
