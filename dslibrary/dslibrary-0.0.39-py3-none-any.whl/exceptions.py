"""
Exception classes.
"""


class DSLibraryException(Exception):
    """
    General errors.
    """


class DSLibraryDataFormatException(DSLibraryException):
    """
    Problems with data
    """
    def __init__(self, message: str, offset: int=None):
        super(DSLibraryDataFormatException, self).__init__(message, offset)
        self.message = message
        self.offset = offset


class DSLibraryCommunicationError(DSLibraryException):
    """
    Communication errors.
    """


