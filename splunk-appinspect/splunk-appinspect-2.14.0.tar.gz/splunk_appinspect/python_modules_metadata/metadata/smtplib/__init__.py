"""
SMTP/ESMTP client class.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
class SMTP:
    """
    This class manages a connection to an SMTP or ESMTP server.
    """

    @tags(TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
    def connect(self):
        """
        Connect to a host on a given port.
        """
        pass


@tags(TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
class LMTP:
    """
    LMTP - Local Mail Transfer Protocol.
    """

    @tags(TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
    def connect(self):
        """
        Connect to the LMTP daemon, on either a Unix or a TCP socket.
        """
        pass
