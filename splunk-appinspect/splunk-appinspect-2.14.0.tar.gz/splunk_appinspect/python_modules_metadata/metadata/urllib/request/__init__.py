"""The urllib.request module defines functions and classes which help in opening URLs"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.HTTP_CONNECTION, TagConsts.PY3_ONLY)
def urlopen():
    """
    create http connection
    """
    pass


@tags(TagConsts.HTTP_CONNECTION, TagConsts.PY3_ONLY)
def urlretrieve():
    """
    create http connection
    """
    pass


@tags(TagConsts.HTTP_CONNECTION, TagConsts.PY3_ONLY)
class URLopener:
    """
    create http connection
    """

    @tags(TagConsts.HTTP_CONNECTION, TagConsts.PY3_ONLY)
    def open(self):
        """
        create http connection
        """
        pass

    @tags(TagConsts.HTTP_CONNECTION, TagConsts.PY3_ONLY)
    def retrieve(self):
        """
        create http connection
        """
        pass


@tags(TagConsts.HTTP_CONNECTION, TagConsts.PY3_ONLY)
class FancyURLopener:
    """
    create http connection
    """

    @tags(TagConsts.HTTP_CONNECTION, TagConsts.PY3_ONLY)
    def open(self):
        """
        create http connection
        """
        pass

    @tags(TagConsts.HTTP_CONNECTION, TagConsts.PY3_ONLY)
    def retrieve(self):
        """
        create http connection
        """
        pass


@tags(TagConsts.HTTP_CONNECTION, TagConsts.PY3_ONLY)
class Request:
    """create http connection"""

    pass
