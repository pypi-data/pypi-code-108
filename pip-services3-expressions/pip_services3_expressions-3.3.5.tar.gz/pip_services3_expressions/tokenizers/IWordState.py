# -*- coding: utf-8 -*-

from abc import ABC

from .ITokenizerState import ITokenizerState


class IWordState(ITokenizerState, ABC):
    """
    Defines an interface for tokenizer state that processes words, identificators or keywords
    """

    def set_word_chars(self, from_symbol: int, to_symbol: int, enable: bool):
        """
        Establish characters in the given range as valid characters for part of a word after
        the first character. Note that the tokenizer must determine which characters are valid
        as the beginning character of a word.

        :param from_symbol: First character index of the interval.
        :param to_symbol: Last character index of the interval.
        :param enable: **True** if this state should use characters in the given range.
        """

    def clear_word_chars(self):
        """
        Clears definitions of word chars.
        """
