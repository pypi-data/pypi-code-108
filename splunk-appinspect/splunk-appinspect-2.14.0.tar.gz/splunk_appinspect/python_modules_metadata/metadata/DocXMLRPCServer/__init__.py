"""
The DocXMLRPCServer module extends the classes found in SimpleXMLRPCServer
to serve HTML documentation in response to HTTP GET requests.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.WEB_SERVER, TagConsts.PY2_ONLY)
class DocXMLRPCServer:
    """
    Create a new server instance. All parameters have the same meaning as for SimpleXMLRPCServer.SimpleXMLRPCServer
    """

    pass
