# -*- coding: utf-8 -*-

from enum import Enum, auto


class TokenType(Enum):
    """
    Types (categories) of tokens such as "number", "symbol" or "word".
    """
    Unknown = 0,
    Eof = auto()
    Eol = auto()
    Float = auto()
    Integer = auto()
    HexDecimal = auto()
    Number = auto()
    Symbol = auto()
    Quoted = auto()
    Word = auto()
    Keyword = auto()
    Whitespace = auto()
    Comment = auto()
    Special = auto()
