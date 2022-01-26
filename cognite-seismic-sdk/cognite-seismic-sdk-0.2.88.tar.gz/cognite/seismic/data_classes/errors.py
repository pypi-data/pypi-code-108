from grpc import StatusCode
from grpc._channel import _InactiveRpcError


class SeismicServiceError(Exception):
    "The base class for all seismic service-related errors."

    def __init__(self, status=None, message=None, hint=None, source=None):
        super().__init__()

        self.status = status
        self.message = message
        self.hint = hint
        self.source = source

    def __repr__(self):
        e = "status: {}\nmessage: {}".format(self.status, self.message)
        if self.hint is not None:
            e += "\nhint: {}".format(self.hint)
        return e

    def __str__(self):
        return self.__repr__()


class NotFoundError(SeismicServiceError):
    "The object was not found."

    def __init__(self, status=None, message=None, hint=None, source=None):
        super().__init__(status, message, hint, source)


class AlreadyExistsError(SeismicServiceError):
    "An object of the same type with the same name or identifier is already present."

    def __init__(self, status=None, message=None, hint=__doc__, source=None):
        super().__init__(status, message, hint, source)


class FailedPreconditionError(SeismicServiceError):
    "The request was rejected because the service or resource state did not allow for the request to be processed."

    def __init__(self, status=None, message=None, hint=__doc__, source=None):
        super().__init__(status, message, hint, source)


class TransientError(SeismicServiceError):
    "A temporary error that can usually be solved by retrying the request."

    def __init__(self, status=None, message=None, source=None):
        super().__init__(status, message, "This is a transient error. Please try again.", source)


class InternalError(SeismicServiceError):
    "An internal error. Please contact support."

    def __init__(self, status=None, message=None, source=None):
        super().__init__(status, message, "Please contact support.", source)


class AuthenticationError(SeismicServiceError):
    "An unauthenticated request was made."

    def __init__(self, status=None, message=None, source=None):
        super().__init__(status, message, "Please check that your api-key or token is valid.", source)


class InvalidArgumentError(SeismicServiceError):
    "An invalid argument was provided."

    def __init__(self, status=None, message=None, source=None):
        super().__init__(status, message, "An argument may be missing, or be the wrong type.", source)


class PermissionError(SeismicServiceError):
    "Insufficient permissions."

    def __init__(self, status=None, message=None, source=None):
        super().__init__(
            status,
            message,
            "Please verify that you have the appropriate capabilities and scope for the operation you are trying to execute.",
            source,
        )


def specialized_error(code: StatusCode):
    if code == StatusCode.NOT_FOUND:
        return NotFoundError
    elif code == StatusCode.ALREADY_EXISTS:
        return AlreadyExistsError
    elif code == StatusCode.FAILED_PRECONDITION:
        return FailedPreconditionError
    elif code == StatusCode.UNAVAILABLE:
        return TransientError
    elif code == StatusCode.INTERNAL:
        return InternalError
    elif code == StatusCode.UNAUTHENTICATED:
        return AuthenticationError
    elif code == StatusCode.INVALID_ARGUMENT:
        return InvalidArgumentError
    elif code == StatusCode.PERMISSION_DENIED:
        return PermissionError
    return SeismicServiceError


def _from_grpc_error(e: _InactiveRpcError):
    se = specialized_error(e.code())()
    se.status = e.code()
    se.message = e.details()
    se.source = e
    return se
