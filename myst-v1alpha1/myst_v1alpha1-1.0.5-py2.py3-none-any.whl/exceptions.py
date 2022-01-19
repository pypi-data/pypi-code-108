"""This modules contains custom Myst exceptions."""


class UnAuthenticatedError(Exception):
    """UnAuthentication error."""

    def __init__(self, message):
        """An `UnAuthenticatedError` is initialized with a message."""
        super(UnAuthenticatedError, self).__init__(message)
        self.message = message


class MystAPIError(Exception):
    """Generic Myst API error."""

    def __init__(self, http_status_code, code, message):
        """A `MystAPIError` is initialized with an HTTP status code, a Myst API code, and a message."""
        super(MystAPIError, self).__init__(message)
        self.http_status_code = http_status_code
        self.code = code
        self.message = message
