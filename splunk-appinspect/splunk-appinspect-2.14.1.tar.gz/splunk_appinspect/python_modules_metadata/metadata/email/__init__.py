"""
The email package is a library for managing email messages, including MIME and other RFC 2822-based message documents.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)

__tags__ = [TagConsts.INET_DATA_HANDLING]


@tags(TagConsts.FILE_READ_AND_WRITE)
def message_from_file(fp):
    """
    Return a message object structure tree from an open file object.
    """
    # parameter is dummy
    pass
