class QException(Exception):
    def __init__(self, msg=None, screen=None, stacktrace=None):
        self.msg = msg
        self.screen = screen
        self.stacktrace = stacktrace

    def __str__(self):
        _msg = f"Message: {self.msg}\n"
        if self.screen is not None:
            _msg += f"Screenshot: available via screen\n"
        if self.stacktrace is not None:
            stacktrace = "\n".join(self.stacktrace)
            _msg += f"Stacktrace:\n{stacktrace}"
        return _msg


class ElementTypeError(QException):
    """
    Find Element types Error
    """
    pass


class NoSuchElementException(QException):
    """
    Element could not found
    """
    pass


class TimeoutException(QException):
    """
    Thrown when a command does not complete in enough time.
    """
    pass
