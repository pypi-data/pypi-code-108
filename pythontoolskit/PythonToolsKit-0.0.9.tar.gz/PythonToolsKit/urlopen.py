#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2022  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements tools to build python package and tools.

>>> from urlopen import urlopen
>>> r = urlopen("http://google.com")
>>> r.code
200
>>> from urlopen import build_opener, httpcode
>>> @httpcode(301)
... def getstatuscode(s, r, f, c, m, h) -> int:
...     return c
...
>>> urlopen = build_opener().open
>>> urlopen("http://google.com")
301
>>>

>>> from urlopen import build_opener, httpcode
>>> @httpcode(200, 500)
... def getstatuscode(s, r, f, c, m, h) -> int:
...     return c
...
>>> urlopen = build_opener().open
>>> urlopen("https://google.com")
200
>>>
"""

__version__ = "0.0.3"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements tools to build python package and tools.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/PythonToolsKit"

copyright = """
PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = ["httpcode", "DefaultHandler", "build_opener"]

from urllib.request import (
    build_opener,
    Request,
    OpenerDirector,
    BaseHandler,
    HTTPRedirectHandler,
    HTTPBasicAuthHandler,
    ProxyBasicAuthHandler,
    DataHandler,
    HTTPHandler,
    HTTPSHandler,
)
from http.client import HTTPResponse, HTTPMessage
from collections import Callable, Sequence
from http import client as httpclient
from urllib.error import HTTPError
from functools import wraps
from typing import Dict

FUNCTIONS_CODES: Dict[int, Callable] = {
    200: lambda s, r, f, c, m, h: f,
    301: HTTPRedirectHandler().http_error_302,
    302: HTTPRedirectHandler().http_error_302,
    303: HTTPRedirectHandler().http_error_302,
    307: HTTPRedirectHandler().http_error_302,
    401: HTTPBasicAuthHandler().http_error_401,
    407: ProxyBasicAuthHandler().http_error_407,
}


def httpcode(*args: Sequence[int]) -> Callable:

    """
    This decorator change action on HTTP error
    code.
    """

    def decorator(function: Callable) -> Callable:

        for code in args:
            FUNCTIONS_CODES[code] = function

        return function

    return decorator


def build_opener(functions: Dict[int, Callable] = None) -> OpenerDirector:

    """
    This function creates an opener object
    using default handlers.
    """

    opener = OpenerDirector()
    add_handler = opener.add_handler

    add_handler(HTTPHandler())
    add_handler(DataHandler())

    if hasattr(httpclient, "HTTPSConnection"):
        add_handler(HTTPSHandler())

    add_handler(DefaultHandler(functions))

    return opener


class DefaultHandler(BaseHandler):

    """
    This class implements the default handler
    for PythonToolsKit.urlopen.urlopen.
    """

    max_repeats = 4
    max_redirections = 10
    auth_header = "Authorization"

    def __init__(self, functions: Dict[int, Callable] = None):
        functions = self.functions = functions or FUNCTIONS_CODES.copy()
        self.functions_get = functions.get

    def httpcode(self, code: int) -> Callable:

        """
        This decorator change action on HTTP error
        code.
        """

        def decorator(function: Callable) -> Callable:

            for code in args:
                FUNCTIONS_CODES[code] = function

            return function

        return decorator

    def http_response(
        self,
        request: Request,
        response: HTTPResponse,
    ) -> None:

        code: int = response.code
        message: str = response.msg
        headers: HTTPMessage = response.info()
        function = self.functions_get(code)

        instance = getattr(function, "__self__", None)

        if instance is not None:
            instance.parent = self.parent
            instance.handler_order = self.handler_order
            args = (request, response, code, message, headers)
        else:
            args = (self, request, response, code, message, headers)

        if function is not None:
            return function(*args)
        else:
            try:
                raise HTTPError(
                    request.full_url, code, message, headers, response
                )
            except HTTPError:
                raise NotImplementedError

    https_response = http_response


urlopen = build_opener(FUNCTIONS_CODES).open
