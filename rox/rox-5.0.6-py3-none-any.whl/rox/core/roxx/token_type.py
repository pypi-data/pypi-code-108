import re

from rox.core.roxx import symbols


class TokenType:
    def __init__(self, text, pattern):
        self.text = text
        self.pattern = re.compile(pattern)


class TokenTypes:
    NOT_A_TYPE = TokenType('NOT_A_TYPE', '')
    STRING = TokenType(symbols.ROXX_STRING_TYPE, r'"((\\.)|[^\\\\"])*"')
    NUMBER = TokenType(symbols.ROXX_NUMBER_TYPE, r'[\-]{0,1}\d+[\.]\d+|[\-]{0,1}\d+')
    BOOLEAN = TokenType(symbols.ROXX_BOOL_TYPE, '%s|%s' % (symbols.ROXX_TRUE, symbols.ROXX_FALSE))
    UNDEFINED = TokenType(symbols.ROXX_UNDEFINED_TYPE, symbols.ROXX_UNDEFINED)

    @staticmethod
    def from_token(token):
        if token is not None:
            tested_token = token.lower()
            for token_type in [TokenTypes.STRING, TokenTypes.NUMBER, TokenTypes.BOOLEAN, TokenTypes.UNDEFINED]:
                if token_type.pattern.match(tested_token):
                    return token_type
        return TokenTypes.NOT_A_TYPE
