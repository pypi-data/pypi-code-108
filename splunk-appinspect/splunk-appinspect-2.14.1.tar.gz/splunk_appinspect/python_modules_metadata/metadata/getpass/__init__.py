"""
Portable password input
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
def getpass():
    """
    Prompt the user for a password without echoing
    """
    pass
