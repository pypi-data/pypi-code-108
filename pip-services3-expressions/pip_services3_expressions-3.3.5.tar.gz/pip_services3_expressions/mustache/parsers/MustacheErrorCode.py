# -*- coding: utf-8 -*-

class MustacheErrorCode:
    """
    General syntax errors.
    """

    # The unknown
    UNKNOWN: str = "UNKNOWN"

    # The internal error
    INTERNAL: str = "INTERNAL"

    # The unexpected end.
    UNEXPECTED_END: str = "UNEXPECTED_END"

    # The error near
    ERROR_NEAR: str = "ERROR_NEAR"

    # The error at
    ERROR_AT: str = "ERROR_AT"

    # The unexpected symbol
    UNEXPECTED_SYMBOL: str = "UNEXPECTED_SYMBOL"

    # The mismatched brackets
    MISMATCHED_BRACKETS: str = "MISMATCHED_BRACKETS"

    # The missing variable
    MISSING_VARIABLE: str = "MISSING_VARIABLE"

    # Not closed section
    NOT_CLOSED_SECTION: str = "NOT_CLOSED_SECTION"

    # Unexpected section end
    UNEXPECTED_SECTION_END: str = "UNEXPECTED_SECTION_END"
