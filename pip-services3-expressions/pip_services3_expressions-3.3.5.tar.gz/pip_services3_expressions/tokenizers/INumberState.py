# -*- coding: utf-8 -*-

from abc import ABC

from .ITokenizerState import ITokenizerState


class INumberState(ITokenizerState, ABC):
    """
    Defines interface for tokenizer state that processes numbers - Integers, Floats, HexDec..
    """
