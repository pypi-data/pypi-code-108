# -*- coding: utf-8 -*-

from pip_services3_expressions.io.StringScanner import StringScanner
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.GenericQuoteState import GenericQuoteState

class TestGenericQuoteState:

    def test_next_token(self):
        state = GenericQuoteState()\

        scanner = StringScanner("'ABC#DEF'#")
        token = state.next_token(scanner, None)
        assert "'ABC#DEF'" == token.value
        assert TokenType.Quoted == token.type

        scanner = StringScanner("'ABC#DEF''")
        token = state.next_token(scanner, None)
        assert "'ABC#DEF'" == token.value
        assert TokenType.Quoted == token.type

    def test_encode_and_decode_string(self):
        state = GenericQuoteState()

        value = state.encode_string("ABC", ord("'"))
        assert "'ABC'" == value

        value = state.decode_string(value, ord("'"))
        assert "ABC" == value

        value = state.decode_string("'ABC'DEF'", ord("'"))
        assert "ABC'DEF" == value

