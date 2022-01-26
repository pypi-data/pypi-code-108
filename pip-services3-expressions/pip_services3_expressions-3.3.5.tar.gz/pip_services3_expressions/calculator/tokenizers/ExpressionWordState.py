# -*- coding: utf-8 -*-
from typing import List

from pip_services3_expressions.io.IScanner import IScanner
from pip_services3_expressions.tokenizers.ITokenizer import ITokenizer
from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.GenericWordState import GenericWordState


class ExpressionWordState(GenericWordState):
    """
    Implements a word state object.
    """

    def __init__(self):
        """
        Constructs an instance of this class.
        """
        super(ExpressionWordState, self).__init__()

        self.keywords: List[str] = [
            "AND", "OR", "NOT", "XOR", "LIKE", "IS", "IN", "NULL", "TRUE", "FALSE"
        ]

        self.clear_word_chars()
        self.set_word_chars(ord('a'), ord('z'), True)
        self.set_word_chars(ord('A'), ord('Z'), True)
        self.set_word_chars(ord('0'), ord('9'), True)
        self.set_word_chars(ord('_'), ord('_'), True)
        self.set_word_chars(0x00c0, 0x00ff, True)
        self.set_word_chars(0x0100, 0xfffe, True)

    def next_token(self, scanner: IScanner, tokenizer: ITokenizer) -> Token:
        """
        Gets the next token from the stream started from the character linked to this state.
        
        :param scanner: A textual string to be tokenized.
        :param tokenizer: A tokenizer class that controls the process.
        :return: The next token from the top of the stream.
        """
        line = scanner.peek()
        column = scanner.peek_column()
        token = super().next_token(scanner, tokenizer)
        value = token.value.upper()

        for keyword in self.keywords:
            if keyword == value:
                return Token(TokenType.Keyword, token.value, line, column)
        return token
