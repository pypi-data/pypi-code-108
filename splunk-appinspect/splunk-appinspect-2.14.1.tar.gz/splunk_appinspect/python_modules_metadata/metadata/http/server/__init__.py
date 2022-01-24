""" This module defines classes for implementing HTTP servers """
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.WEB_SERVER, TagConsts.PY3_ONLY)
class HttpServer(object):
    """This class builds on the TCPServer class by storing the server address as instance variables named server_name and server_port."""

    pass


@tags(TagConsts.WEB_SERVER, TagConsts.PY3_ONLY)
class ThreadingHTTPServer(object):
    """This class is identical to HTTPServer but uses threads to handle requests by using the ThreadingMixIn."""

    pass
