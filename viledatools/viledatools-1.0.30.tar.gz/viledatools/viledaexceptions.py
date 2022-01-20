# coding=utf-8
"""
(C) FHCS GmbH

Custom exception classes
"""

class ImportCellParserException(Exception):
    """
    Raised when parsing specific errors in ImportCellParser occur
    """
    def __init__(self, message):
        self.message = message


class ImportSheetParserException(Exception):
    """
    Raised when parsing specific errors in ImportSheetParser occur
    """
    def __init__(self, message):
        self.message = message
