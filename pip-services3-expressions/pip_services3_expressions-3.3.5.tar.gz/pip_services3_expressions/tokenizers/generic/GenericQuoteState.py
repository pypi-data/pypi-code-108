# -*- coding: utf-8 -*-
from typing import Optional

from pip_services3_expressions.io.IScanner import IScanner
from pip_services3_expressions.tokenizers.IQuoteState import IQuoteState
from pip_services3_expressions.tokenizers.ITokenizer import ITokenizer
from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.utilities.CharValidator import CharValidator


class GenericQuoteState(IQuoteState):
    """
    A quoteState returns a quoted string token from a scanner. This state will collect characters
    until it sees a match to the character that the tokenizer used to switch to this state.
    For example, if a tokenizer uses a double-quote character to enter this state,
    then :func:`next_token <GenericQuoteState.next_token>` will search for another double-quote until it finds one
    or finds the end of the scanner.
    """

    def next_token(self, scanner: IScanner, tokenizer: ITokenizer) -> Token:
        """
        Return a quoted string token from a scanner. This method will collect
        characters until it sees a match to the character that the tokenizer used
        to switch to this state.
        
        :param scanner: A textual string to be tokenized.
        :param tokenizer: A tokenizer class that controls the process.
        :return: The next token from the top of the stream.
        """
        first_symbol = scanner.read()
        token_value = chr(first_symbol)
        line = scanner.peek_line()
        column = scanner.peek_column()

        next_symbol = scanner.read()
        while not CharValidator.is_eof(next_symbol):
            token_value = token_value + chr(next_symbol)
            if next_symbol == first_symbol:
                break
            next_symbol = scanner.read()

        return Token(TokenType.Quoted, token_value, line, column)

    def encode_string(self, value: str, quote_symbol: int) -> Optional[str]:
        """
        Encodes a string value.

        :param value: A string value to be encoded.
        :param quote_symbol: A string quote character.
        :return: An encoded string.
        """
        if value is None:
            return None
        result = chr(quote_symbol) + value + chr(quote_symbol)
        return result

    def decode_string(self, value: str, quote_symbol: int) -> Optional[str]:
        """
        Decodes a string value.
        
        :param value: A string value to be decoded.
        :param quote_symbol: A string quote character.
        :return: An decoded string.
        """
        if value is None:
            return None

        if len(value) >= 2 and ord(value[0]) == quote_symbol and ord(value[len(value) - 1]) == quote_symbol:
            return value[1:len(value) - 1]

        return value
