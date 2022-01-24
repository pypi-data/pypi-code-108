import logging
from typing import Union, List, Any, Dict, Optional
from http import HTTPStatus

LOG = logging.getLogger(__name__)


# --- REST API Response Errors mapping to 4xx status codes --- #
class HttpResponseError(Exception):
    def __init__(
        self,
        message: str,
        code: int,
        data: Optional[Union[List[str], Dict[str, Any]]] = None,
    ) -> None:
        self.data = data
        self.message = message
        self.code = code
        if self.data and not self.message:
            self.message = "A problem has been encountered while processing the request"
        LOG.error("[%s]: %s\n%s", self.code, self.message, self.data)
        super().__init__(self.message)


class InternalServerError(HttpResponseError):
    def __init__(self, message: str, data: Optional[Union[List[str], Dict[str, Any]]] = None) -> None:
        super().__init__(message, code=HTTPStatus.INTERNAL_SERVER_ERROR, data=data)


class BadRequestError(HttpResponseError):
    def __init__(self, message: str, data: Optional[Union[List[str], Dict[str, Any]]] = None) -> None:
        super().__init__(message, code=HTTPStatus.BAD_REQUEST, data=data)


class UnauthorizedError(HttpResponseError):
    def __init__(self, message: str, data: Optional[Union[List[str], Dict[str, Any]]] = None) -> None:
        super().__init__(message, code=HTTPStatus.UNAUTHORIZED, data=data)


class ForbiddenError(HttpResponseError):
    def __init__(self, message: str, data: Optional[Union[List[str], Dict[str, Any]]] = None) -> None:
        super().__init__(message, code=HTTPStatus.FORBIDDEN, data=data)


class NotFoundError(HttpResponseError):
    def __init__(self, message: str, data: Optional[Union[List[str], Dict[str, Any]]] = None) -> None:
        super().__init__(message, code=HTTPStatus.NOT_FOUND, data=data)


class MethodNotAllowedError(HttpResponseError):
    def __init__(self, message: str, data: Optional[Union[List[str], Dict[str, Any]]] = None) -> None:
        super().__init__(message, code=HTTPStatus.METHOD_NOT_ALLOWED, data=data)


class NotAcceptableError(HttpResponseError):
    def __init__(self, message: str, data: Optional[Union[List[str], Dict[str, Any]]] = None) -> None:
        super().__init__(message, code=HTTPStatus.NOT_ACCEPTABLE, data=data)


class RequestTimeoutError(HttpResponseError):
    def __init__(self, message: str, data: Optional[Union[List[str], Dict[str, Any]]] = None) -> None:
        super().__init__(message, code=HTTPStatus.REQUEST_TIMEOUT, data=data)


class ConflictError(HttpResponseError):
    def __init__(self, message: str, data: Optional[Union[List[str], Dict[str, Any]]] = None) -> None:
        super().__init__(message, code=HTTPStatus.CONFLICT, data=data)


class GoneError(HttpResponseError):
    def __init__(self, message: str, data: Optional[Union[List[str], Dict[str, Any]]] = None) -> None:
        super().__init__(message, code=HTTPStatus.GONE, data=data)


class PreconditionFailedError(HttpResponseError):
    def __init__(self, message: str, data: Optional[Union[List[str], Dict[str, Any]]] = None) -> None:
        super().__init__(message, code=HTTPStatus.PRECONDITION_FAILED, data=data)


class PayloadTooLargeError(HttpResponseError):
    def __init__(self, message: str, data: Optional[Union[List[str], Dict[str, Any]]] = None) -> None:
        super().__init__(message, code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE, data=data)


# ------------------------------------------------------------ #


# --- Misc REST Utility Errors --- #
class RequestObjectError(BadRequestError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class QueryParamMissingError(RequestObjectError):
    def __init__(self, expected: Union[str, List[str]], actual: List[str]):
        super().__init__(f'Could not find query parameter "{expected}" in {actual}')


class RequestObjectMalformedError(RequestObjectError):
    def __init__(self, missing: str) -> None:
        super().__init__(f'"request" object malformed, missing "{missing}" property')


class RequestObjectMissingUserInfoError(RequestObjectError):
    def __init__(self, missing: Union[List[str], str]) -> None:
        if isinstance(missing, list):
            keys = '", "'.join(missing)
        else:
            keys = missing
        super().__init__(f'"request" object missing required user info key(s): "{keys}"')


# -------------------------------- #

# --- System Route Errors --- #
class FileFailedToCompileError(BadRequestError):
    def __init__(self, data: List[str]) -> None:
        msg = "The file failed to compile.  See 'error_details' for more info"
        super().__init__(message=msg, data=data)


# --------------------------- #


# --- Auth0 & Token Errors --- #
class Auth0Error(UnauthorizedError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class TokenExpiredError(Auth0Error):
    def __init__(self) -> None:
        super().__init__("Token is expired")


class InvalidAudienceError(Auth0Error):
    def __init__(self) -> None:
        super().__init__("Invalid audience")


class InvalidTokenSignatureError(Auth0Error):
    def __init__(self) -> None:
        super().__init__("Token signature is invalid")


class InvalidIssuedAtError(Auth0Error):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class TokenRefreshError(Auth0Error):
    def __init__(self, message: str) -> None:
        super().__init__(message)


# ---------------------------- #


# --- Access Control Errors --- #
class AccessControlError(UnauthorizedError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class UserInformationMissingError(AccessControlError):
    def __init__(self) -> None:
        super().__init__("User profile information not found")


# -------------------------------- #
