"""This module supports writing XML-RPC client code"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.XML_RPC_CONNECTION, TagConsts.PY3_ONLY)
class ServerProxy:
    """A ServerProxy instance is an object that manages communication with a remote XML-RPC server"""

    pass
