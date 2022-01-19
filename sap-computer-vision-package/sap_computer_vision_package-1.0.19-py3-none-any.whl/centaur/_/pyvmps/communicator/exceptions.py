class SendMessageException(Exception):
    """Raise when exception is raised in send method"""


class UnmarshallException(Exception):
    """Raised when error encountered trying to unmarshall socket byte string to pyvmp message"""


class MarshallException(Exception):
    """Raised when error encountered trying to marshall pyvmp message to socket byte string"""
