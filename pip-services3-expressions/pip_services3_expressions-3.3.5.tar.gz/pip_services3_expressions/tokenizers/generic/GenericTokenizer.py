# -*- coding: utf-8 -*-

from pip_services3_expressions.tokenizers.AbstractTokenizer import AbstractTokenizer
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.GenericCommentState import GenericCommentState
from pip_services3_expressions.tokenizers.generic.GenericNumberState import GenericNumberState
from pip_services3_expressions.tokenizers.generic.GenericQuoteState import GenericQuoteState
from pip_services3_expressions.tokenizers.generic.GenericSymbolState import GenericSymbolState
from pip_services3_expressions.tokenizers.generic.GenericWhitespaceState import GenericWhitespaceState
from pip_services3_expressions.tokenizers.generic.GenericWordState import GenericWordState


class GenericTokenizer(AbstractTokenizer):
    """
    Implements a default tokenizer class.
    """

    def __init__(self):
        super(GenericTokenizer, self).__init__()

        self.symbol_state = GenericSymbolState()
        self.symbol_state.add("<>", TokenType.Symbol)
        self.symbol_state.add("<=", TokenType.Symbol)
        self.symbol_state.add(">=", TokenType.Symbol)

        self.number_state = GenericNumberState()
        self.quote_state = GenericQuoteState()
        self.whitespace_state = GenericWhitespaceState()
        self.word_state = GenericWordState()
        self.comment_state = GenericCommentState()

        self.clear_character_states()
        self.set_character_state(0x0000, 0x00ff, self.symbol_state)
        self.set_character_state(0x0000, ord(' '), self.whitespace_state)

        self.set_character_state(ord('a'), ord('z'), self.word_state)
        self.set_character_state(ord('A'), ord('Z'), self.word_state)
        self.set_character_state(0x00c0, 0x00ff, self.word_state)
        self.set_character_state(0x0100, 0xfffe, self.word_state)

        self.set_character_state(ord('-'), ord('-'), self.number_state)
        self.set_character_state(ord('0'), ord('9'), self.number_state)
        self.set_character_state(ord('.'), ord('.'), self.number_state)

        self.set_character_state(ord('\"'), ord('\"'), self.quote_state)
        self.set_character_state(ord('\''), ord('\''), self.quote_state)

        self.set_character_state(ord('#'), ord('#'), self.comment_state)
