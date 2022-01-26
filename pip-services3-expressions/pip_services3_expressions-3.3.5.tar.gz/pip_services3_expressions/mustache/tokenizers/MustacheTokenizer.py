# -*- coding: utf-8 -*-
from typing import Union, Optional

from pip_services3_expressions.mustache.tokenizers.MustacheSpecialState import MustacheSpecialState
from pip_services3_expressions.tokenizers.AbstractTokenizer import AbstractTokenizer
from pip_services3_expressions.tokenizers.ICommentState import ICommentState
from pip_services3_expressions.tokenizers.INumberState import INumberState
from pip_services3_expressions.tokenizers.ITokenizerState import ITokenizerState
from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.GenericQuoteState import GenericQuoteState
from pip_services3_expressions.tokenizers.generic.GenericSymbolState import GenericSymbolState
from pip_services3_expressions.tokenizers.generic.GenericWhitespaceState import GenericWhitespaceState
from pip_services3_expressions.tokenizers.generic.GenericWordState import GenericWordState


class MustacheTokenizer(AbstractTokenizer):

    def __init__(self):
        """
        Constructs this object with default parameters.
        """
        super(MustacheTokenizer, self).__init__()

        self.__special = True
        self.__special_state: Union[ITokenizerState, None] = None

        self.symbol_state = GenericSymbolState()
        self.symbol_state.add("{{", TokenType.Symbol)
        self.symbol_state.add("}}", TokenType.Symbol)
        self.symbol_state.add("{{{", TokenType.Symbol)
        self.symbol_state.add("}}}", TokenType.Symbol)

        self.number_state: Union[INumberState, None] = None
        self.quote_state = GenericQuoteState()
        self.whitespace_state = GenericWhitespaceState()
        self.word_state = GenericWordState()
        self.comment_state: Union[ICommentState, None] = None
        self.__special_state = MustacheSpecialState()

        self.clear_character_states()
        self.set_character_state(0x0000, 0x00ff, self.symbol_state)
        self.set_character_state(0x0000, ord(' '), self.whitespace_state)

        self.set_character_state(ord('a'), ord('z'), self.word_state)
        self.set_character_state(ord('A'), ord('Z'), self.word_state)
        self.set_character_state(ord('0'), ord('9'), self.word_state)
        self.set_character_state(ord('_'), ord('_'), self.word_state)
        self.set_character_state(0x00c0, 0x00ff, self.word_state)
        self.set_character_state(0x0100, 0xfffe, self.word_state)

        self.set_character_state(ord('\"'), ord('\"'), self.quote_state)
        self.set_character_state(ord('\''), ord('\''), self.quote_state)

        self.skip_whitespaces = True
        self.skip_comments = True
        self.skip_eof = True

    def _read_next_token(self) -> Optional[Token]:
        if self._scanner is None:
            return None

        # Check for initial state
        if self._next_token is None and self._last_token_type == TokenType.Unknown:
            self.__special = True

        # Process quotes
        if self.__special:
            token = self.__special_state.next_token(self._scanner, self)
            if token is not None and token.value != '':
                return token

        # Process other tokens
        self.__special = False
        token = super()._read_next_token()
        # Switch to quote when '{{' or '{{{' symbols found
        if token is not None and (token.value == "}}" or token.value == "}}}"):
            self.__special = True

        return token
