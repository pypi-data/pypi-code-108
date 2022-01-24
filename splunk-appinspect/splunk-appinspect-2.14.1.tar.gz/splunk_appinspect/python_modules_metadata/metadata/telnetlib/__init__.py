"""
TELNET client class. Based on RFC 854: TELNET Protocol Specification.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
class Telnet:
    """
    Telnet interface class. An instance of this class represents a connection to a telnet server.
    """

    @tags(TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
    def open(self):
        """
        Connect to a host.
        """
        pass
