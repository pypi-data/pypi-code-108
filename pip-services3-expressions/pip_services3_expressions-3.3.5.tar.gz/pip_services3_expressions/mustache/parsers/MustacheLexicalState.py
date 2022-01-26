# -*- coding: utf-8 -*-

from enum import Enum, auto


class MustacheLexicalState(Enum):
    """
    Define states in mustache lexical analysis.
    """
    Value = 0
    Operator1 = auto()
    Operator2 = auto()
    Variable = auto()
    Comment = auto()
    Closure = auto()
