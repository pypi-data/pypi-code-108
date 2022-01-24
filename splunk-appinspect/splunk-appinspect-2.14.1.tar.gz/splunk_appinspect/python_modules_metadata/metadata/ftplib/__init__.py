"""
An FTP client class and some helper functions.
Based on RFC 959: File Transfer Protocol (FTP).
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
class FTP:
    """
    FTP client class.
    """

    @tags(TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
    def connect(self):
        """
        Connect to host.
        """
        pass
