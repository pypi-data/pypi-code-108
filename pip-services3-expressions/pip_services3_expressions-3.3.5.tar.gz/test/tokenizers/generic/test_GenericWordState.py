# -*- coding: utf-8 -*-

from pip_services3_expressions.io.StringScanner import StringScanner
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.GenericWordState import GenericWordState


class TestGenericWordState:

    def test_next_token(self):
        state = GenericWordState()

        scanner = StringScanner("AB_CD=")
        token = state.next_token(scanner, None)
        assert "AB_CD" == token.value
        assert TokenType.Word == token.type
