"""
create http connection
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.HTTP_CONNECTION)
def urlopen():
    """
    create http connection
    """
    pass


@tags(TagConsts.HTTP_CONNECTION)
class Request:
    """
    create http connection
    """

    pass
