import socket
from http.client import HTTPException
from suds.transport import TransportError
from urllib.error import HTTPError


class MicrosoftAdvertisingAccountLostAccessException(Exception):
    """ Raised when we cannot access to an account """
    pass


MICROSOFT_EXCEPTIONS_TO_RETRY = (
    socket.timeout,
    ConnectionResetError,
    HTTPException,
    TransportError,
    HTTPError
)
