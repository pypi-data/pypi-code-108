# -*- coding: utf-8 -*-

from pip_services3_expressions.io.StringScanner import StringScanner
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.GenericNumberState import GenericNumberState


class TestGenericNumberState:

    def test_next_token(self):
        state = GenericNumberState()

        scanner = StringScanner("ABC")
        failed = False
        try:
            state.next_token(scanner, None)
        except Exception as e:
            failed = True
        assert failed is True

        scanner = StringScanner("123#")
        token = state.next_token(scanner, None)
        assert '123' == token.value
        assert TokenType.Integer == token.type

        scanner = StringScanner("-123#")
        token = state.next_token(scanner, None)
        assert '-123' == token.value
        assert TokenType.Integer == token.type

        scanner = StringScanner("123.#")
        token = state.next_token(scanner, None)
        assert '123.' == token.value
        assert TokenType.Float == token.type

        scanner = StringScanner("123.456#")
        token = state.next_token(scanner, None)
        assert '123.456' == token.value
        assert TokenType.Float == token.type

        scanner = StringScanner("-123.456#")
        token = state.next_token(scanner, None)
        assert '-123.456' == token.value
        assert TokenType.Float == token.type
