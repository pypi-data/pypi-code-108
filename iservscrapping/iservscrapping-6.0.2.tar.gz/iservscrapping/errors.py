"""
The MIT License (MIT)
Copyright (c) Alwin Lohrie (Niwla23)
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
Errors that can be thrown by the iservscrapping module.
"""
# pylint: disable=unnecessary-pass


class IservError(BaseException):
    """
    This exception is never actually thrown. All exceptions inherit from it so it can be used to catch all iserv errors.
    """
    pass


class LoginError(IservError):
    """
    This is raised when the login fails. Since iserv is to dumb to use http conventions, we need to check this by text.
    (It does not return anything but 200, even on not found or failed auth). Login therefore currently only works
     on german instances.
    """
    pass


class WrongContentError(IservError):
    """
    This is raised when the text the scrapper got is not the text it expected. Happens when wrong URLs are passed since
    Iserv does not use HTTP status codes (see LoginError)
    """
    pass
