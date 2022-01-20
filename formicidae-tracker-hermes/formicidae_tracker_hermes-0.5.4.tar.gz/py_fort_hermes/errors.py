""" Various Errors returned by py_fort_hermes Contexts

"""

from enum import Enum


class ErrorCode(Enum):
    """Enumeration for internal error code

    """
    FH_NO_ERROR = 0
    """No errors occured"""
    FH_STREAM_NO_HEADER = 10001
    """The stream or file has no header"""
    FH_STREAM_WRONG_VERSION = 10002
    """The stream has an unsupported version"""
    FH_END_OF_STREAM = 10003
    """The stream reached the end"""
    FH_MESSAGE_DECODE_ERROR = 10004
    """The next message could not be decoded"""
    FH_COULD_NOT_CONNECT = 10005
    """could not connect to host"""
    FH_SOCKET_ERROR = 10006
    """network error"""
    FH_UNEXPECTED_END_OF_FILE_SEQUENCE = 10007
    """an error occured before the end of a file sequence"""


class InternalError(Exception):
    """Internal error raised by py_fort_hermes.

    Attributes:
        code (int): the ErrorCode for the internal error

    """

    def __init__(self, code: ErrorCode, message):
        self.message = message
        self.code = code
        super().__init__(self.message)


class UnexpectedEndOfFileSequence(Exception):
    """The reading of a sequence of file was interrupted by an error

    Attributes:
        segmentPath (str): the segment where the error occured

    """

    def __init__(self, what, segmentPath):
        self.segmentPath = segmentPath
        self.message = "Unexpected end of file sequence in '%s': %s" % (
            segmentPath, what)
        super().__init__(self.message)
