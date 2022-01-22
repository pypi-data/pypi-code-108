class ApiError(Exception):
    """
    Base for api errors
    """


class InvalidOrMissingParameters(ApiError):
    """
    Raised when mattermost returns a
    400 Invalid or missing parameters in URL or request body
    """


class NoAccessTokenProvided(ApiError):
    """
    Raised when mattermost returns a
    401 No access token provided
    """


class NotEnoughPermissions(ApiError):
    """
    Raised when mattermost returns a
    403 Do not have appropriate permissions
    """


class ResourceNotFound(ApiError):
    """
    Raised when mattermost returns a
    404 Resource not found
    """


class MethodNotAllowed(ApiError):
    """
    Raised when mattermost returns a
    405 Method Not Allowed
    """


class ContentTooLarge(ApiError):
    """
    Raised when mattermost returns a
    413 Content too large
    """


class TooManyRequests(ApiError):
    """
    Raised when mattermost returns a
    429 Too many requests
    """


class InternalServerError(ApiError):
    """
    Raised when mattermost returns a
    500 Internal Server Error
    """


class FeatureDisabled(ApiError):
    """
    Raised when mattermost returns a
    501 Feature is disabled
    """
