import asyncio


class Error(Exception):
    """Base exception for this module"""

    pass


class BackendNotFoundError(Exception):
    pass


class MaxConcurrencyError(Error):
    pass


class NoResponderError(Error):
    """Exception to raise when there is no responder on a given subject"""

    pass


class NoServerError(Error):
    """Exception to raise when no server is reachable"""


class MaxPayloadError(Error):
    """Exception to raise when request payload is too big"""

    pass


class TimeoutError(asyncio.TimeoutError):
    """Exception raised in case of timeout"""

    pass


class ConnectionClosedError(Error):
    pass


class ConnectionNotStartedError(ConnectionClosedError):
    pass


class ConnectionDrainingError(Error):
    pass


class ConnectionReconnectingError(Error):
    pass


class ConnectionBrokenError(Error):
    pass


class InvalidSubjectError(Error):
    pass


class InvalidTimeoutError(Error):
    pass


class InvalidCallbackError(Error):
    pass


class InvalidHeadersError(Error):
    pass


class SubscriptionClosedError(Error):
    pass


class SubscriptionNotStartedError(SubscriptionClosedError):
    pass


class RouterNotStartedError(Error):
    pass


class RouterStoppedError(Error):
    pass


class AbortResponseError(Error):
    pass
