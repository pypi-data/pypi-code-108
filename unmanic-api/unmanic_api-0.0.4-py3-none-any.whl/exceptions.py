"""Exceptions for Unmanic."""


class UnmanicError(Exception):
    """Generic Unmanic Exception."""

    pass


class UnmanicBadRequestRequestedEndpointNotFoundError(UnmanicError):
    """Unmanic bad request endpoint not found exception."""

    pass


class UnmanicBadRequestRequestedMethodNotAllowedError(UnmanicError):
    """Unmanic bad request method not allowed exception."""

    pass


class UnmanicBadRequestValidationError(UnmanicError):
    """Unmanic bad request validation error exception."""

    pass


class UnmanicConnectionError(UnmanicError):
    """Unmanic connection exception."""

    pass


class UnmanicInternalServerError(UnmanicError):
    """Unmanic internal server error exception."""

    pass
