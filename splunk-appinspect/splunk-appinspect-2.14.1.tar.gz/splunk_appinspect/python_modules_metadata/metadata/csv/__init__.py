"""
manipulate csv files
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.FILE_READ_AND_WRITE)
def writer():
    """
    create a new csv writer object
    """
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def reader():
    """
    create a new csv reader object
    """
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
class DictWriter:
    """
    create a csv dict writer object
    """

    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
class DictReader:
    """
    create a csv dict reader object
    """

    pass
