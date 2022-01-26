# -*- coding: utf-8 -*-

from pip_services3_expressions.calculator.tokenizers.ExpressionNumberState import ExpressionNumberState
from pip_services3_expressions.calculator.tokenizers.ExpressionQuoteState import ExpressionQuoteState
from pip_services3_expressions.calculator.tokenizers.ExpressionSymbolState import ExpressionSymbolState
from pip_services3_expressions.calculator.tokenizers.ExpressionWordState import ExpressionWordState
from pip_services3_expressions.tokenizers.AbstractTokenizer import AbstractTokenizer
from pip_services3_expressions.tokenizers.generic.CppCommentState import CppCommentState
from pip_services3_expressions.tokenizers.generic.GenericWhitespaceState import GenericWhitespaceState


class ExpressionTokenizer(AbstractTokenizer):
    """
    Implement tokenizer to perform lexical analysis for expressions.
    """

    def __init__(self):
        """
        Constructs an instance of this class.
        """
        super(ExpressionTokenizer, self).__init__()

        self.decode_strings = False

        self.whitespace_state = GenericWhitespaceState()

        self.symbol_state = ExpressionSymbolState()
        self.number_state = ExpressionNumberState()
        self.quote_state = ExpressionQuoteState()
        self.word_state = ExpressionWordState()
        self.comment_state = CppCommentState()

        self.clear_character_states()
        self.set_character_state(0x0000, 0xfffe, self.symbol_state)
        self.set_character_state(0, ord(' '), self.whitespace_state)

        self.set_character_state(ord('a'), ord('z'), self.word_state)
        self.set_character_state(ord('A'), ord('Z'), self.word_state)
        self.set_character_state(0x00c0, 0x00ff, self.word_state)
        self.set_character_state(ord('_'), ord('_'), self.word_state)

        self.set_character_state(ord('0'), ord('9'), self.number_state)
        self.set_character_state(ord('-'), ord('-'), self.number_state)
        self.set_character_state(ord('.'), ord('.'), self.number_state)

        self.set_character_state(ord('"'), ord('"'), self.quote_state)
        self.set_character_state(ord('\''), ord('\''), self.quote_state)

        self.set_character_state(ord('/'), ord('/'), self.comment_state)
