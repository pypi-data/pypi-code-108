from functools import wraps
import grpc
from grpc_status import rpc_status
from continual.rpc.rpc import error_details_pb2
from typing import TypeVar, Optional, Dict


def map_to_dict(msg) -> dict:
    """Converts SalarMapContainer to dict."""
    return dict(msg.items())


class BaseException(Exception):
    """Base exception for Continual APIs.

    Wraps underlying API errors.
    """

    message: str
    """Error message."""

    details: Dict[str, str]
    """Error details dictionary.
    
    Details includes things like field level validation errors.
    """

    def __init__(self, message: str = "", details: Optional[Dict[str, str]] = None):
        self.message = message
        self.details = map_to_dict(details or dict())
        super().__init__(message, details)


class OtherError(BaseException):
    """Unknown error status."""


class InternalError(BaseException):
    """Internal server error.

    Please contact support if this error persists.
    """


class InvalidArgumentError(BaseException):
    """Invalid argument error.

    Details includes field level error messages.
    """


class AlreadyExistsError(BaseException):
    """Already exists error.

    The resource cannot be created because it already exists.
    """


class NotFoundError(BaseException):
    """Not found error.

    The resource does not exist.
    """


# PermissionDenied means the action was denied due to permissions error.
class PermissionDeniedError(BaseException):
    """Permission denied error.

    The caller does not have the necessary permissions to take an action.
    """


# Unauthenticated means the request does not have valid authentication information.
class UnauthenticatedError(BaseException):
    """Unauthenticated error.

    The caller is not authenticated.
    """


class FailedError(BaseException):
    """Failed error.

    A long-running operation entered a failed state.
    """


class UnsupportedError(BaseException):
    """Unsupported error.

    An operation or field is not supported.
    """


class FailedPreconditionError(BaseException):
    """Failed precondition error.

    A precondition for this operation was not satisfied.
    """


def normalize_exceptions(func):
    """Function decorator for catching common errors and
    re-raising as Continual exception."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except grpc.RpcError as err:
            info = error_details_pb2.ErrorDetails()
            status = rpc_status.from_call(err)
            if (
                status is not None
                and status.details is not None
                and len(status.details) > 0
            ):
                detail = status.details[0]
                if detail.Is(error_details_pb2.ErrorDetails.DESCRIPTOR):
                    detail.Unpack(info)
            msg = err.details()

            if err.code() == grpc.StatusCode.INTERNAL:
                raise InternalError(msg, info.details) from None
            elif err.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise InvalidArgumentError(msg, info.details) from None
            elif err.code() == grpc.StatusCode.ALREADY_EXISTS:
                raise AlreadyExistsError(msg, info.details) from None
            elif err.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(msg, info.details) from None
            elif err.code() == grpc.StatusCode.PERMISSION_DENIED:
                raise PermissionDeniedError(msg, info.details)
            elif err.code() == grpc.StatusCode.UNAUTHENTICATED:
                raise UnauthenticatedError(msg, info.details) from None
            elif err.code() == grpc.StatusCode.FAILED_PRECONDITION:
                raise FailedPreconditionError(msg, info.details) from None
            else:
                raise OtherError(msg, info.details) from None

    return wrapper


T = TypeVar("T")


def normalize_exceptions_for_class(x: T) -> T:
    """Wraps all methods in a class instance with an to exception handler.

    This is used to wrap raw GRPC API stubs and normalize all exceptions.
    """
    method_list = [func for func in dir(x) if callable(getattr(x, func))]
    for method in method_list:
        if not method.startswith("__"):
            setattr(x, method, normalize_exceptions(getattr(x, method)))
    return x
