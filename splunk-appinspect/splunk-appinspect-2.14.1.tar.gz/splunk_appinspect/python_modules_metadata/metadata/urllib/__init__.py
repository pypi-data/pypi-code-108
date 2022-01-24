"""
create http connection
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)

from . import request  # noqa: F401


@tags(TagConsts.HTTP_CONNECTION)
def urlopen():
    """
    create http connection
    """
    pass


@tags(TagConsts.HTTP_CONNECTION)
def urlretrieve():
    """
    create http connection
    """
    pass


@tags(TagConsts.HTTP_CONNECTION)
class URLopener:
    """
    create http connection
    """

    @tags(TagConsts.HTTP_CONNECTION)
    def open(self):
        """
        create http connection
        """
        pass

    @tags(TagConsts.HTTP_CONNECTION)
    def open_http(self):
        """
        create http connection
        """
        pass

    @tags(TagConsts.HTTP_CONNECTION)
    def open_data(self):
        """
        create http connection
        """
        pass

    @tags(TagConsts.HTTP_CONNECTION)
    def retrieve(self):
        """
        create http connection
        """
        pass


@tags(TagConsts.HTTP_CONNECTION)
class FancyURLopener:
    """
    create http connection
    """

    @tags(TagConsts.HTTP_CONNECTION)
    def open(self):
        """
        create http connection
        """
        pass

    @tags(TagConsts.HTTP_CONNECTION)
    def open_http(self):
        """
        create http connection
        """
        pass

    @tags(TagConsts.HTTP_CONNECTION)
    def open_data(self):
        """
        create http connection
        """
        pass

    @tags(TagConsts.HTTP_CONNECTION)
    def retrieve(self):
        """
        create http connection
        """
        pass
