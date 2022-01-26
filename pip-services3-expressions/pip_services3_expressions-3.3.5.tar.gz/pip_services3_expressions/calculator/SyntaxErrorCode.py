# -*- coding: utf-8 -*-

class SyntaxErrorCode:
    """
    General syntax errors.
    """

    # The unknown
    UNKNOWN: str = 'UNKNOWN'
    # The internal error
    INTERNAL: str = 'INTERNAL'
    # The unexpected end.
    UNEXPECTED_END: str = 'UNEXPECTED_END'
    # The error near
    ERROR_NEAR: str = 'ERROR_NEAR'
    # The error at
    ERROR_AT: str = 'ERROR_AT'
    # The unknown symbol
    UNKNOWN_SYMBOL: str = 'UNKNOWN_SYMBOL'
    # The missed close parenthesis
    MISSED_CLOSE_PARENTHESIS: str = 'MISSED_CLOSE_PARENTHESIS'
    # The missed close square bracket
    MISSED_CLOSE_SQUARE_BRACKET: str = 'MISSED_CLOSE_SQUARE_BRACKET'

