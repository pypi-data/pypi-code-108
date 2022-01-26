# -*- coding: utf-8 -*-
from typing import List

from pip_services3_expressions.mustache.parsers.MustacheTokenType import MustacheTokenType


class MustacheToken:
    """
    Defines a mustache token holder.
    """

    def __init__(self, type: MustacheTokenType, value: str, line: int, column: int):
        """
        Creates an instance of a mustache token.

        :param type: a token type.
        :param value: a token value.
        :param line: a line number where the token is.
        :param column: a column number where the token is.
        """
        self.__type = type
        self.__value = value
        self.__tokens = []
        self.__line = line
        self.__column = column

    @property
    def type(self)->MustacheTokenType:
        """
        Gets the token value or variable name.
        """
        return self.__type

    @property
    def value(self)->str:
        """
        Gets the token value or variable name.
        """
        return self.__value

    @property
    def tokens(self)->List['MustacheToken']:
        """
        Gets a list of subtokens is this token a section.
        """
        return self.__tokens

    @property
    def line(self)->int:
        """
        The line number where the token is.
        """
        return self.__line

    @property
    def column(self)->int:
        """
        The column number where the token is.
        """
        return self.__column
