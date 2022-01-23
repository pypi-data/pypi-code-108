class ZbError(Exception):
    """
    The base class for all `Zb` specific errors.
    """


class ZbServerError(ZbError):
    """
    Represents a `Zb` specific 500 series HTTP error.
    """

    def __init__(self, status, message, headers):
        self.status = status
        self.message = message
        self.headers = headers


class ZbClientError(ZbError):
    """
    Represents a `Zb` specific 400 series HTTP error.
    """

    def __init__(self, status, message, headers):
        self.status = status
        self.message = message
        self.headers = headers


class ZbOperationError(ZbError):
    """
    Represents a `Zb` application logical error.
    """

    def __init__(self, status, message):
        self.status = status
        self.message = message
