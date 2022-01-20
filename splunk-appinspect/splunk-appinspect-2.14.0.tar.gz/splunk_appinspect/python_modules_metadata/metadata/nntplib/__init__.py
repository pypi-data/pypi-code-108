"""
An NNTP client class based on RFC 977: Network News Transfer Protocol.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
class NNTP:
    """
    NNTP client class.
    """

    pass
