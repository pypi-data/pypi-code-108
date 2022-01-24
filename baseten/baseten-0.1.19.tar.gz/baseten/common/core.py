import functools
from enum import Enum

from requests import RequestException


class Error(Exception):
    """Base Baseten Error"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class AuthorizationError(Error):
    """Raised in places where the user needs to be logged in and is not."""
    pass


class FrameworkNotSupportedError(Error):
    """Raised in places where the user attempts to use Baseten with an unsupported framework"""
    pass


class ModelNotSupportedError(Error):
    """Raised when a user attempts to use unsupported models for a
    framework that is otherwise supported"""
    pass


class ModelFilesMissingError(Error):
    """Raised when a user attempts to deploy a model which requires supporting files."""
    pass


class ModelClassImplementationError(Error):
    """Raised when a user attempts to deploy a model class which does not implement necessary methods."""
    pass


class ModelInputShapeError(Error):
    """Raised when deploying a model whose input shape doesn't match the number of feature names given by the user."""
    pass


class SampleDataInputShapeError(Error):
    """Raised when deploying a model whose input shape doesn't match the number of feature names given by the user."""
    pass


class ApiError(Error):
    """Errors in calling the Baseten API."""
    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response

    def __str__(self):
        error_str = self.message
        if self.response is not None:  # non-200 Response objects are falsy, hence the not None.
            error_str = f'{error_str}\n<Server response: {self.response.content}>'
        return error_str


def raises_api_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RequestException as err:
            raise ApiError(f'Error calling {func.__name__}.', response=err.response) from err
    return wrapper


class Semver(Enum):
    MAJOR = 'MAJOR'
    MINOR = 'MINOR'
    PATCH = 'PATCH'


MODEL_FILENAME = 'model'
ARTIFACT_FILENAME = 'artifact'
