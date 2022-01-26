# -*- coding: utf-8 -*-
from pip_services3_expressions.io.IScanner import IScanner
from pip_services3_expressions.tokenizers.ITokenizer import ITokenizer
from pip_services3_expressions.tokenizers.ITokenizerState import ITokenizerState
from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.utilities.CharValidator import CharValidator


class MustacheSpecialState(ITokenizerState):
    """
    Implements a quote string state object for Mustache templates.
    """

    __Bracket: str = ord("{")

    def next_token(self, scanner: IScanner, tokenizer: ITokenizer) -> Token:
        """
        Gets the next token from the stream started from the character linked to this state.

        :param scanner: A textual string to be tokenized.
        :param tokenizer: A tokenizer class that controls the process.
        :return: The next token from the top of the stream.
        """
        line = scanner.peek_line()
        column = scanner.peek_column()
        token_value = ""

        next_symbol = scanner.read()
        while not CharValidator.is_eof(next_symbol):
            if next_symbol == MustacheSpecialState.__Bracket:
                if scanner.peek() == MustacheSpecialState.__Bracket:
                    scanner.unread()
                    break
            token_value = token_value + chr(next_symbol)

            next_symbol = scanner.read()

        return Token(TokenType.Special, token_value, line, column)
