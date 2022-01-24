class EmptyLineException(Exception):
    """Empty line"""
    pass


class IncorrectLineException(Exception):
    """Incorrect variable string"""
    pass


class BadStatusException(Exception):
    """Incorrect server response status"""

    def __init__(self, status, message):
        self.status = status
        self.message = message
