import http
from typing import List

from tktl.core.exceptions.base import (
    TaktileCliError,
    TaktileRuntimeError,
    TaktileSdkError,
)


class TimeoutError(TaktileCliError):
    pass


class EndpointInstantiationError(TaktileRuntimeError):
    pass


class AuthenticationError(TaktileSdkError):
    pass


class UnlazifiedParquetError(TaktileRuntimeError):
    pass


class UnsupportedInputTypeException(TaktileSdkError):
    pass


class MissingDocker(TaktileCliError):
    pass


class ValidationException(TaktileRuntimeError):
    pass


class ProjectValidationException(TaktileCliError):
    pass


class HTTPException(Exception):  # TODO - Potential Cleanup
    def __init__(self, status_code: int, detail: str = None) -> None:
        if detail is None:
            detail = http.HTTPStatus(status_code).phrase
        self.status_code = status_code
        self.detail = detail

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"


class APISwitchException(TaktileSdkError):
    # TODO: Remove this in taktile-cli 1.0
    pass


class APIClientException(HTTPException):
    pass

    def __str__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"


class APIClientExceptionRetryable(APIClientException):
    pass


class UserRepoValidationException(TaktileCliError):
    def __init__(
        self, missing_files: List, missing_directories: List, missing_config: bool
    ):
        self.missing_files = missing_files
        self.missing_directories = missing_directories
        self.missing_config = missing_config


class NoContentsFoundException(UserRepoValidationException):
    pass


def validate_config(fn):
    from tktl.core.managers.project import ProjectManager

    def wrapper(*args, **kwargs):
        if ProjectManager.get_config() is None:
            raise TaktileCliError(
                "No configuration found. Are you sure you have a tktl.yaml file in "
                "your current directory? Run tktl init to start a new project"
            )
        return fn(*args, **kwargs)

    return wrapper
