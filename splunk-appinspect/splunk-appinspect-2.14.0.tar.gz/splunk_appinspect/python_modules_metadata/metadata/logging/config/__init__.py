"""
The functions defined in this module configure the logging module.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
def dictConfig():
    """
    Takes the logging configuration from a dictionary.
    """
    pass


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
def fileConfig():
    """
    Reads the logging configuration from a configparser-format file named fname.
    """
    pass
