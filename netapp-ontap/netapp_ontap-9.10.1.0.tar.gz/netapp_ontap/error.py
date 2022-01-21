# pylint: disable=line-too-long
"""
Copyright &copy; 2021 NetApp Inc. All rights reserved.

This module defines the custom exception type. All exceptions raised by
the library descend from this type.
"""

from typing import Optional  # pylint: disable=unused-import

from netapp_ontap.response import NetAppResponse


# Error message that is called when a user hits either a MemoryError or OverflowError
# when trying to send large files via a multipart/form-data post/patch through
# the requests library.
FILE_SIZE_WARNING = (
    "One of the file(s) you are trying to upload may be too large. Install these"
    " additional dependencies to handle the large file upload and try again."
    "\npip install requests[security]"
)


class NetAppRestError(Exception):
    """Common base class for all exceptions raised by the library functions. All
    custom exceptions are derived from this type.
    """

    def __init__(self, message: str = None, cause: Exception = None) -> None:
        """Initalize the error object.

        Optionally accepts a custom message and cause. If provided, the cause is
        the exception object that was handled when this exception is created.

        Args:
            message: A human readable message that explains the error.
            cause: An exception object that caused this exception to be raised.
        """

        msg = message if message else ""
        if cause:
            self.cause = cause
            msg += f" Caused by {cause!r}"
            if getattr(cause, "response", None) is not None:
                try:
                    self._response = NetAppResponse(cause.response)  # type: ignore
                    err_msg = cause.response.json().get("error", {}).get("message")  # type: ignore
                    if err_msg:
                        msg += f": {err_msg}"
                except Exception:  # pylint: disable=broad-except
                    # the error response wasn't json so there's nothing additional
                    # we will add
                    pass

        super().__init__(msg.strip())

    @property
    def http_err_response(self) -> Optional[NetAppResponse]:
        """Describes a response to an API request that contains an error.

        Returns:
            Response object if the exception was raised because of an API failure (HTTP status code of 400 or higher). None if the exception was not related to an API error.
        """

        return getattr(self, "_response", None)

    @property
    def status_code(self) -> Optional[int]:
        """Return the status code of the HTTP response if this error was generated
        from a failed HTTP request. Otherwise, returns None
        """

        if not getattr(self, "_response", None):
            return None

        return self._response.http_response.status_code

    @property
    def response_body(self) -> Optional[dict]:
        """Return the HTTP response body if this error was generated from a failed
        HTTP request. The body will be in dictionary form. If this exception is
        not from a failed request or the body cannot be parsed as JSON, returns None
        """

        if not getattr(self, "_response", None):
            return None

        try:
            return self._response.http_response.json()
        except ValueError:
            return None

    @property
    def response_text(self) -> Optional[str]:
        """Return the HTTP response body if this error was generated from a failed
        HTTP request. This will be the raw text of the response body. This is useful
        when the response body cannot be parsed as JSON.
        """

        if not getattr(self, "_response", None):
            return None

        return self._response.http_response.text
