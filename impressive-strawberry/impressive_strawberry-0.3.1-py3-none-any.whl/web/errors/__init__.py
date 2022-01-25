"""
This module contains the possible errors that can be raised by :mod:`impressive_strawberry`, and then possibly be caught by one of the :mod:`impressive_strawberry.handlers`.
"""

import fastapi

from impressive_strawberry.web import models

__all__ = (
    "StrawberryException",
    "MissingAuthHeader",
    "InvalidAuthHeader",
    "WrongAuthHeader",
    "ResourceNotFound",
    "MultipleResultsFound",
    "DuplicatingUnrepeatableUnlock",
)


class StrawberryException(Exception):
    """
    Base class for :mod:`impressive_strawberry` exceptions.
    """

    STATUS_CODE: int = 500
    ERROR_CODE: str = "UNKNOWN"
    REASON: str = "Unknown error, please report this as a bug to the Impressive Strawberry developers."

    @classmethod
    def to_model(cls) -> models.error.StrawberryErrorModel:
        return models.error.StrawberryErrorModel(error_code=cls.ERROR_CODE, reason=cls.REASON)

    @classmethod
    def to_response(cls) -> fastapi.Response:
        return fastapi.Response(content=cls.to_model().json(), status_code=cls.STATUS_CODE, media_type="application/json")


class MissingAuthHeader(StrawberryException):
    STATUS_CODE = 401
    ERROR_CODE = "MISSING_AUTH_HEADER"
    REASON = "The Authorization header is missing."


class InvalidAuthHeader(StrawberryException):
    STATUS_CODE = 401
    ERROR_CODE = "INVALID_AUTH_HEADER"
    REASON = "The provided Authorization header is invalid."


class WrongAuthHeader(StrawberryException):
    STATUS_CODE = 401
    ERROR_CODE = "WRONG_AUTH_HEADER"
    REASON = "The value provideed in the Authorization header is in a valid format, but its value is incorrect."


class ResourceNotFound(StrawberryException):
    STATUS_CODE = 404
    ERROR_CODE = "NOT_FOUND"
    REASON = "The requested resource was not found. Either it does not exist, or you are not authorized to view it."


class MultipleResultsFound(StrawberryException):
    STATUS_CODE = 500
    ERROR_CODE = "MULTIPLE_FOUND"
    REASON = "Multiple resources were found with the requested identifier. This is probably a problem in the Impressive Strawberry database. If you are the system admininistrator, ensure you have run all the available migrations through Alembic."


class DuplicatingUnrepeatableUnlock(StrawberryException):
    STATUS_CODE = 406
    ERROR_CODE = "DUPLICATING_UNLOCK"
    REASON = "The achievement has already been unlocked by the user and its not repeatable."
