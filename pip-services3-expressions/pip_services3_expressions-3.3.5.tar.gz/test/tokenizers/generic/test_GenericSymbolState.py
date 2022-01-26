# -*- coding: utf-8 -*-

from pip_services3_expressions.io.StringScanner import StringScanner
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.GenericSymbolState import GenericSymbolState


class TestGenericSymbolState:

    def test_next_token(self):
        state = GenericSymbolState()
        state.add("<", TokenType.Symbol)
        state.add("<<", TokenType.Symbol)
        state.add("<>", TokenType.Symbol)

        scanner = StringScanner("<A<<<>")

        token = state.next_token(scanner, None)
        assert "<" == token.value
        assert TokenType.Symbol == token.type

        token = state.next_token(scanner, None)
        assert "A" == token.value
        assert TokenType.Symbol == token.type

        token = state.next_token(scanner, None)
        assert "<<" == token.value
        assert TokenType.Symbol == token.type

        token = state.next_token(scanner, None)
        assert "<>" == token.value
        assert TokenType.Symbol == token.type
