"""This module defines classes which implement the client side of the HTTP and HTTPS protocols"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.HTTP_CONNECTION, TagConsts.PY3_ONLY)
class HTTPConnection(object):
    """An HTTPConnection instance represents one transaction with an HTTP server"""

    pass
