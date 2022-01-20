"""
This module implements a simple HTTP server (based on BaseHTTPServer) that serves WSGI applications
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.WEB_SERVER)
def make_server():
    """
    Create a new WSGI server listening on host and port, accepting connections for app.
    """
    pass


@tags(TagConsts.WEB_SERVER)
class WSGIServer:
    """
    Create a WSGIServer instance. server_address should be a (host,port) tuple
    """

    pass
