# -*- coding: utf-8 -*-
from pip_services3_expressions.calculator.parsers.ExpressionTokenType import ExpressionTokenType
from pip_services3_expressions.variants.Variant import Variant


class ExpressionToken:
    """
    Defines an expression token holder.
    """

    def __init__(self, type: ExpressionTokenType, value: Variant, line: int, column: int):
        """
        Creates an instance of this token and initializes it with specified values.
        
        :param type: The type of this token.
        :param value: The value of this token.
        :param line: the line number where the token is.
        :param column: the column number where the token is.
        """
        self.__type = type
        self.__value = value
        self.__line = line
        self.__column = column

    @property
    def type(self) -> ExpressionTokenType:
        """
        The type of this token.
        """
        return self.__type

    @property
    def value(self) -> Variant:
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
