"""
A generic class to build line-oriented command interpreters.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.EXTERNAL_COMMAND_EXECUTION)
class Cmd:
    """
    A Cmd instance or subclass instance is a line-oriented interpreter framework.
    """

    pass
