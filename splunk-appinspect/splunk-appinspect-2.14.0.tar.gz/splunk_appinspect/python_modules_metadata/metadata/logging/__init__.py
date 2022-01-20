"""
logging module
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)

from . import config, handlers  # noqa: F401


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
class StreamHandler:
    """
    Sends logging output to streams such as sys.stdout, sys.stderr or any file-like object
    """

    pass


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
class FileHandler:
    """
    Sends logging output to a disk file.
    """

    pass
