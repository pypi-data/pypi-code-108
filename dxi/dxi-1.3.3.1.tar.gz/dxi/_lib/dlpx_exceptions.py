"""
Custom exception class for delphixpy scripts
"""
from dxi._lib import dx_logging as log

class DlpxException(BaseException):
    """
    Delphix Exception class. Exit signals are handled by calling method.
    """

    def __init__(self, error):
        super(DlpxException, self).__init__(error)
        self._error = error

    @property
    def error(self):
        """
        Return an DlpxException object describing this error.
        """
        log.print_exception(self.error)
        return self.error


class DlpxObjectNotFound(BaseException):
    """
    Delphix Exception class. Exit signals are handled by calling method.
    Raised when a Delphix Object is not found
    """

    def __init__(self, message):
        super(DlpxObjectNotFound, self).__init__(message)
        log.print_exception(message)
        self._message = message

    @property
    def message(self):
        """
        Return an ErrorResult object describing this request message.
        """
        return self._message


class DlpxObjectExists(BaseException):
    """
    Delphix Exception class. Exit signals are handled by calling method.
    Raised when a Delphix Object is found
    """

    def __init__(self, message):
        super(DlpxObjectExists, self).__init__(message)
        log.print_exception(message)
        self._message = message

    @property
    def message(self):
        """
        Return an ErrorResult object describing this request message.
        """
        return self._message


class DXIException(BaseException):
    """
    Delphix DXI Exception class.
    Exit signals are handled by calling method.
    This is the superclass for all DXI Exceptions.
    """

    def __init__(self, message, code=None):
        super(DXIException, self).__init__(message)
        log.print_exception(message)
        self._message = message
        self._code = code

    @property
    def message(self):
        """
        Return an ErrorResult object describing this request message.
        """
        return self._message

    @property
    def code(self):
        """
        Return an object  describing this error message's code.
        """
        return self._code