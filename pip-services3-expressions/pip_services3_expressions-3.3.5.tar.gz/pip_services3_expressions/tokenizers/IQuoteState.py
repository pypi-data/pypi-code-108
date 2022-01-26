# -*- coding: utf-8 -*-

from abc import ABC

from .ITokenizerState import ITokenizerState


class IQuoteState(ITokenizerState, ABC):
    """
    Defines an interface for tokenizer state that processes quoted strings.
    """

    def encode_string(self, value: str, quote_symbol: int) -> str:
        """
        Encodes a string value.

        :param value: A string value to be encoded.
        :param quote_symbol: A string quote character.
        :return: An encoded string.
        """

    def decode_string(self, value: str, quote_symbol: int) -> str:
        """
        Decodes a string value.
        
        :param value: A string value to be decoded.
        :param quote_symbol: A string quote character.
        :return: An decoded string.
        """
