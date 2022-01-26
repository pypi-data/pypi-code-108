# -*- coding: utf-8 -*-

from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.GenericSymbolState import GenericSymbolState


class ExpressionSymbolState(GenericSymbolState):
    """
    Constructs an instance of this class.
    """

    def __init__(self):
        super(ExpressionSymbolState, self).__init__()

        self.add("<=", TokenType.Symbol)
        self.add(">=", TokenType.Symbol)
        self.add("<>", TokenType.Symbol)
        self.add("!=", TokenType.Symbol)
        self.add(">>", TokenType.Symbol)
