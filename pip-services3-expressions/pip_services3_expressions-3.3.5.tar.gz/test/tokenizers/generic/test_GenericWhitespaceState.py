# -*- coding: utf-8 -*-

from pip_services3_expressions.io.StringScanner import StringScanner
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.GenericWhitespaceState import GenericWhitespaceState


class TestGenericWhitespaceState:

    def test_next_token(self):
        state = GenericWhitespaceState()

        scanner = StringScanner(" \t\n\r #")
        token = state.next_token(scanner, None)
        assert " \t\n\r " == token.value
        assert TokenType.Whitespace == token.type
