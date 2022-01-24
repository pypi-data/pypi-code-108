"""
IMAP4 client. Based on RFC 2060.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
class IMAP4:
    """
    IMAP4 client class.
    """

    @tags(TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
    def open(self):
        """
        Setup connection to remote server.
        """
        pass


@tags(TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
class IMAP4_stream:
    """
    IMAP4 client class over a stream.
    """

    @tags(TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
    def open(self):
        """Setup a stream connection."""
        pass
