"""
xmlrpclib unsafe operations, it's dangerous to get untrusted data from network
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.XML_RPC_CONNECTION)
class ServerProxy:
    """
    A logical connection to an XML-RPC server
    """

    pass
