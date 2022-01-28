"""Module for creating custom exceptions."""


class AuthError(Exception):
    """Exception raised if authentication fails."""

    pass


class ResultCodeException(Exception):
    """Exception raised if failed to add a ResultCode."""

    pass
