# -*- coding: utf-8 -*-
from typing import Any

from pip_services3_expressions.tokenizers.TokenType import TokenType


class Token:
    """
    A token represents a logical chunk of a string. For example, a typical tokenizer would break
    the string "1.23 &lt;= 12.3" into three tokens: the number 1.23, a less-than-or-equal symbol,
    and the number 12.3. A token is a receptacle, and relies on a tokenizer to decide precisely how
    to divide a string into tokens.
    """

    def __init__(self, type: TokenType, value: str, line: int, column: int):
        """
        Constructs this token with type and value.

        :param type: The type of this token.
        :param value: The token string value.
        :param line: The line number where the token is.
        :param column: The column number where the token is.
        """
        self.__type = type
        self.__value = value
        self.__line = line
        self.__column = column

    @property
    def type(self) -> TokenType:
        """
        The token type.
        """
        return self.__type

    @property
    def value(self) -> str:
        """
        The token value.
        """
        return self.__value

    @property
    def line(self) -> int:
        """
        The line number where the token is.
        """
        return self.__line

    @property
    def column(self) -> int:
        """
        The column number where the token is.
        """
        return self.__column

    def equals(self, obj: Any) -> bool:
        if isinstance(obj, Token):
            token = obj
            return token.__type == self.__type and token.__value == self.__value
