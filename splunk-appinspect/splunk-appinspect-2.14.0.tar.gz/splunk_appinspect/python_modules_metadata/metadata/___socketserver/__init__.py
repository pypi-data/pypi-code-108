"""
The SocketServer module simplifies the task of writing network servers.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.WEB_SERVER, TagConsts.PY3_ONLY)
class TCPServer:
    """
    This uses the Internet TCP protocol, which provides for continuous streams of data between the client and server
    """

    pass


@tags(TagConsts.WEB_SERVER, TagConsts.PY3_ONLY)
class UDPServer:
    """
    This uses datagrams, which are discrete packets of information that may arrive out of order or be lost while in transit.
    """

    pass
