"""
A POP3 client class. Based on the J. Myers POP3 draft.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
class POP3:
    """POP3 client class."""

    pass
