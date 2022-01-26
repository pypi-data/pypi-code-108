# -*- coding: utf-8 -*-

from enum import Enum, auto


class MustacheTokenType(Enum):
    """
    Define types of mustache tokens.
    """
    Unknown = 0
    Value = auto()
    Variable = auto()
    EscapedVariable = auto()
    Section = auto()
    InvertedSection = auto()
    SectionEnd = auto()
    Partial = auto()
    Comment = auto()
