from abc import ABC
from typing import Tuple

from ..communication import JchessMessage, ErrorType, JchessMessageType


class ClientError(Exception, ABC):
    pass


class UnhandledMessageError(ClientError):

    def __init__(self, message: JchessMessage):
        super(UnhandledMessageError, self).__init__(f"Message of hype {message.message_type} was unhandled")
        self._message = message


class LoginFailedError(ClientError):
    def __init__(self):
        super(LoginFailedError, self).__init__("Login Failed")


class WrongMessageType(ClientError):
    def __init__(self, message: JchessMessage, expected_type: Tuple[JchessMessageType, ...]):
        super(WrongMessageType, self).__init__(
            f"Expected message one of type {', '.join(str(x) for x in expected_type)} but got {message.message_type}"
        )
        self._message = message


class InterruptClient(Exception):
    def __init__(self, error: ErrorType):
        super(InterruptClient, self).__init__(f"Interruption called from error {error}")
        self._error = error

    @property
    def error(self) -> ErrorType:
        return self._error
