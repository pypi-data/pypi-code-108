"""
third party module requests usage
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.HTTP_CONNECTION)
def get():
    """
    http get method usage
    """
    pass


@tags(TagConsts.HTTP_CONNECTION)
def put():
    """
    http put method usage
    """
    pass


@tags(TagConsts.HTTP_CONNECTION)
def post():
    """
    http post method usage
    """
    pass


@tags(TagConsts.HTTP_CONNECTION)
def request():
    """
    http request with requests
    """
    pass


@tags(TagConsts.HTTP_CONNECTION)
def head():
    """
    http head method usage
    """
    pass


@tags(TagConsts.HTTP_CONNECTION)
def path():
    """
    http request with requests
    """
    pass


@tags(TagConsts.HTTP_CONNECTION)
def delete():
    """
    http delete method usage
    """
    pass


class Session:
    """
    create a http session
    """

    @tags(TagConsts.HTTP_CONNECTION)
    def get(self):
        """
        http get method usage
        """
        pass

    @tags(TagConsts.HTTP_CONNECTION)
    def put(self):
        """
        http put method usage
        """
        pass

    @tags(TagConsts.HTTP_CONNECTION)
    def post(self):
        """
        http post method usage
        """
        pass

    @tags(TagConsts.HTTP_CONNECTION)
    def head(self):
        """
        http head method usage
        """
        pass

    @tags(TagConsts.HTTP_CONNECTION)
    def delete(self):
        """
        http delete method usage
        """
        pass

    @tags(TagConsts.HTTP_CONNECTION)
    def path(self):
        """
        http request with requests
        """
        pass

    @tags(TagConsts.HTTP_CONNECTION)
    def request(self):
        """
        http call with request
        """
        pass


@tags(TagConsts.HTTP_CONNECTION)
class Request:
    """
    Request class in requests
    """

    pass
