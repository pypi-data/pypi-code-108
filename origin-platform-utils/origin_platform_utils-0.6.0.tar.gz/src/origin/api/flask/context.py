from typing import Dict
from flask import request
from functools import cached_property

from origin.api.context import Context


class FlaskContext(Context):
    """
    Flask-specific context.
    """

    @cached_property
    def headers(self) -> Dict[str, str]:
        """
        :returns: HTTP request headers
        """
        return dict(request.headers)

    @cached_property
    def cookies(self) -> Dict[str, str]:
        """
        :returns: HTTP request cookies
        """
        return request.cookies
