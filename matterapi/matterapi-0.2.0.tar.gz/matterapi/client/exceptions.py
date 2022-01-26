from typing import Optional

from pydantic import BaseModel


class ExceptionBody(BaseModel):
    id: str
    message: str
    request_id: str
    status_code: int
    detailed_error: Optional[str]
    is_oauth: Optional[bool]


class ApiError(Exception):
    """
    Base for api errors
    """

    def __init__(self, message, error_details: ExceptionBody = None):
        super().__init__(message)
        self.details = error_details


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
