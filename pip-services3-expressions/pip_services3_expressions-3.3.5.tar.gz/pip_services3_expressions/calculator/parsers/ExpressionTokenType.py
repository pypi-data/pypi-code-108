# -*- coding: utf-8 -*-

from enum import Enum, auto


class ExpressionTokenType(Enum):
    """
    Define types of expression tokens.
    """
    Unknown = 0
    LeftBrace = auto()
    RightBrace = auto()
    LeftSquareBrace = auto()
    RightSquareBrace = auto()
    Plus = auto()
    Minus = auto()
    Star = auto()
    Slash = auto()
    Percent = auto()
    Power = auto()
    Equal = auto()
    NotEqual = auto()
    More = auto()
    Less = auto()
    EqualMore = auto()
    EqualLess = auto()
    ShiftLeft = auto()
    ShiftRight = auto()
    And = auto()
    Or = auto()
    Xor = auto()
    Is = auto()
    In = auto()
    NotIn = auto()
    Element = auto()
    Null = auto()
    Not = auto()
    Like = auto()
    NotLike = auto()
    IsNull = auto()
    IsNotNull = auto()
    Comma = auto()
    Unary = auto()
    Function = auto()
    Variable = auto()
    Constant = auto()
