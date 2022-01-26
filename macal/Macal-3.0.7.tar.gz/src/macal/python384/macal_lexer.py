#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_lexer.py                                                                #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 Language Lexer                                                                        #
#                                                                                                 #
###################################################################################################

"""Lexer implementation"""

from string import whitespace

from .macal_variable_types import BOOL, FLOAT, INT, STRING
from .macal_lextokentypes import IDENTIFIER, KEYWORD, OP_AND, OP_OR, COMMENT
from .macal_keywords import Keywords, TRUE, FALSE, NIL, AND, OR
from .macal_lextoken import LexToken
from .macal_lextokentypes import SINGLE_TOKENS, DOUBLE_TOKENS
from .macal_exceptions import LexException

# https://www.youtube.com/watch?v=52dhJwnZ2qs

__version__ = '3.0.1'

class MacalTokenizer:
    def __init__(self):
        self.source: str = ""
        self.length: int = 0
        self.version: str = __version__

    def lex(self, source: str) -> list:
        self.source = source
        self.length = len(source)
        tokens = []
        line = 0
        offset = 0
        position = 0
        (token, next_position, next_line, next_offset) = self.lex_token(position, line, offset)
        while token is not None:
            tokens.append(token)
            (token, next_position, next_line, next_offset) = self.lex_token(next_position, next_line, next_offset)
        return tokens

    def lex_current(self, position: int, line: int, offset: int) -> (str, int, int, int):
        if position >= self.length:
            return (None, position, line, offset)
        return (self.source[position], position, line, offset)

    def lex_next(self, position: int, line: int, offset: int) -> (str, int, int, int):
        (current, next_position, next_line, next_offset) = self.lex_current(position + 1, line, offset + 1)
        if current is not None and current == '\n':
            next_offset = 0
            next_line = next_line + 1
        return (current, next_position, next_line, next_offset)

    def skip_whitespace(self, position: int, line: int, offset: int) -> (str, int, int, int):
        (current, next_position, next_line, next_offset) = self.lex_current(position, line, offset)
        while current is not None and current in whitespace:
            (current, next_position, next_line, next_offset) = self.lex_next(next_position, next_line, next_offset)
        return (current, next_position, next_line, next_offset)

    def lex_token(self, position: int, line: int, offset: int) -> (LexToken, int, int, int):
        (current, next_position, next_line, next_offset) = self.skip_whitespace(position, line, offset)
        if current is None:
            return (None, next_position, next_line, next_offset)
        if current.isalpha():
            return self.lex_identifier(next_position, next_line, next_offset)
        if current.isdigit():
            return self.lex_number(next_position, next_line, next_offset)
        if current == '"' or current == "'":
            return self.lex_string(next_position, next_line, next_offset)
        return self.lex_shorts(next_position, next_line, next_offset)

    def lex_identifier(self, position: int, line: int, offset: int) -> (LexToken, int, int, int):
        (current, next_position, next_line, next_offset) = self.lex_current(position, line, offset)
        while current is not None and (current.isalpha() or current == '_' or current.isdigit()):
            (current, next_position, next_line, next_offset) = self.lex_next(next_position, next_line, next_offset)
        ident = self.source[position:next_position]
        tt = IDENTIFIER
        if ident in (TRUE, FALSE):
            tt = BOOL
        elif ident == NIL:
            tt = NIL
        elif ident in Keywords:
            tt = KEYWORD
        elif ident == AND:
            tt = OP_AND
        elif ident == OR:
            tt = OP_OR
        return (LexToken(tt, ident, position, line, offset),
                next_position, next_line, next_offset)

    def lex_number(self, position: int, line: int, offset: int) -> (LexToken, int, int, int):
        (current, next_position, next_line, next_offset) = self.lex_current(position, line, offset)
        points = 0
        while current is not None and (current.isdigit() or current == '.'):
            if current == '.':
                points += 1
            if points > 1:
                raise LexException("Multiple decimal points found in float", next_line, next_offset)
            (current, next_position, next_line, next_offset) = self.lex_next(next_position, next_line, next_offset)
        return (LexToken(INT if points == 0 else FLOAT, 
            int(self.source[position:next_position]) if points == 0 else float(self.source[position:next_position]), 
            position, line, offset), next_position, next_line, next_offset)

    @staticmethod
    def apply_escapes(source: str) -> str:
        index = 0
        length = len(source)
        destination = "";
        while index < length:
            if source[index] == '\\' and index+1 < length:
                if (source[index+1] in ['a','b','n','r','t','0']):
                    if source[index+1] == 'a':
                        destination=f"{destination}\a"
                    elif source[index+1] == 'b':
                        destination=f"{destination}\b"
                    elif source[index+1] == 'n':
                        destination=f"{destination}\n"
                    elif source[index+1] == 'r':
                        destination=f"{destination}\r"
                    elif source[index+1] == 't':
                        destination=f"{destination}\t"
                    else:
                        destination=f"{destination}\0"
                else:
                    destination = f"{destination}{source[index+1]}"
                index += 1
            else:
                destination=f"{destination}{source[index]}"
            index += 1
        return destination

    def lex_string(self, position: int, line: int, offset: int) -> (LexToken, int, int, int):
        (current, next_position, next_line, next_offset) = self.lex_current(position, line, offset)
        terminator = current
        (current, next_position, next_line, next_offset) = self.lex_next(next_position, next_line, next_offset)
        escaped = False
        while current is not None and True if current != terminator else escaped:
            escaped = current == '\\'
            (current, next_position, next_line, next_offset) = self.lex_next(next_position, next_line, next_offset)
        if current is None:
            raise LexException("Unexpected end of file in string", next_line, next_offset)
        (_, next_position, next_line, next_offset) = self.lex_next(next_position, next_line, next_offset)
        return (LexToken(STRING, self.apply_escapes(self.source[(position+1):(next_position-1)]), position, line, offset),
            next_position, next_line, next_offset)

    def lex_shorts(self, position: int, line: int, offset: int) -> (LexToken, int, int, int):
        (current, next_position, next_line, next_offset) = self.lex_current(position, line, offset)
        if current in SINGLE_TOKENS:
            (_, next_position, next_line, next_offset) = self.lex_next(next_position, next_line, next_offset)
            return (LexToken(SINGLE_TOKENS[current], current, position, line, offset),
                next_position, next_line, next_offset)
        elif next_position < self.length:
            return self.lex_doubles(position, line, offset)
        return (LexToken(None, current, position, line, offset),
                    next_position, next_line, next_offset)    

    def lex_doubles(self, position: int, line: int, offset: int) -> (LexToken, int, int, int):
        (current, next_position, next_line, next_offset) = self.lex_current(position, line, offset)
        (next_char, next_char_position, next_char_line, next_char_offset) = self.lex_next(next_position, next_line, next_offset)
        double = f"{current}{next_char}"
        if double in DOUBLE_TOKENS:
            (_, next_char_position, next_char_line, next_char_offset) = self.lex_next(next_char_position, next_char_line, next_char_offset)
            if DOUBLE_TOKENS[double] == COMMENT:
                return self.lex_comment_short(next_char_position, next_char_line, next_char_offset)
            else:
                return (LexToken(DOUBLE_TOKENS[double], double, position, line, offset),
                    next_char_position, next_char_line, next_char_offset)
        elif current in DOUBLE_TOKENS:
            return (LexToken(DOUBLE_TOKENS[current], current, position, line, offset),
                next_char_position, next_char_line, next_char_offset)
        else:
            raise LexException(f"Invalid character sequence ({double}).", line, offset)
        return (LexToken(None, current, position, line, offset),
                    next_position, next_line, next_offset)

    def lex_comment_short(self, position: int, line: int, offset: int) -> (LexToken, int, int, int):
        (current, next_position, next_line, next_offset) = self.lex_current(position, line, offset)
        while current is not None and current != '\n':
            (current, next_position, next_line, next_offset) = self.lex_next(next_position, next_line, next_offset)
        (_, next_position, next_line, next_offset) = self.lex_next(next_position, next_line, next_offset)
        return (LexToken(COMMENT, self.source[position:next_position], position, line, offset),
                    next_position, next_line, next_offset)
