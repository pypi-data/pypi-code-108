class ImportSetupException(Exception):
    """Base exception for the document states app"""


class ImportSetupActionError(ImportSetupException):
    """Raise for errors during execution of import setup actions"""
