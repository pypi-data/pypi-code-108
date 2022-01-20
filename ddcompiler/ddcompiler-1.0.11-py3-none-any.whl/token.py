from enum import Enum


class TokenType(Enum):
    END_OF_EXPRESSION = -1
    VARIABLE = 1
    STRING = 2
    NUMBER = 3
    # Comparison operators
    EQ = 11
    NOTEQ = 12
    LT = 13
    LTEQ = 14
    GT = 15
    GTEQ = 16
    # Binary Boolean operators
    AND = 21
    OR = 22
    NOT = 23
    # Boolean constants
    TRUE = 31
    FALSE = 32
    # Parenthesis
    LPAREN = 41
    RPAREN = 42
    COMMA = 43
    # functions returning boolean
    CONTAINS = 51
    STARTSWITH = 52
    ENDSWITH = 53
    # functions returning string
    LOWER = 54
    UPPER = 55
    # function returning number
    LEN = 56


class Token:
    def __init__(self, ttext, ttype):
        # token text for token types VARIABLE, STRING and NUMBER is
        # necessary; for other token types it is kind-of redundant
        self.ttext = ttext
        self.ttype = ttype

    token_map = {
        "and": TokenType.AND,
        "or": TokenType.OR,
        "not": TokenType.NOT,
        "True": TokenType.TRUE,
        "False": TokenType.FALSE,
        "contains": TokenType.CONTAINS,
        "startswith": TokenType.STARTSWITH,
        "endswith": TokenType.ENDSWITH,
        "lower": TokenType.LOWER,
        "upper": TokenType.UPPER,
        "len": TokenType.LEN,
    }

    @staticmethod
    def get_token(ttext):
        if ttext in Token.token_map:
            return Token(ttext, Token.token_map[ttext])
        raise ValueError(f"Error during lexical analysis: '{ttext}' not a supported token")
