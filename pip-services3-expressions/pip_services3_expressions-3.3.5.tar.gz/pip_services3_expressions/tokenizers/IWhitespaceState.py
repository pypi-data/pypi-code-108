# -*- coding: utf-8 -*-

from abc import ABC

from .ITokenizerState import ITokenizerState


class IWhitespaceState(ITokenizerState, ABC):
    """
    Defines an interface for tokenizer state that processes whitespaces (' ', '\t')
    """

    def set_whitespace_chars(self, from_symbol: int, to_symbol: int, enable: bool):
        """
        Establish the given characters as whitespace to ignore.
        
        :param from_symbol: First character index of the interval.
        :param to_symbol: Last character index of the interval.
        :param enable: **true** if this state should ignore characters in the given range.
        """

    def clear_whitespace_chars(self):
        """
        Clears definitions of whitespace characters.
        """
