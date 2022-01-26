# -*- coding: utf-8 -*-

from pip_services3_expressions.io.StringScanner import StringScanner
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.CppCommentState import CppCommentState


class TestCppCommentState:

    def test_next_token(self):
        state = CppCommentState()

        scanner = StringScanner("-- Comment \n Comment ")
        failed = False

        try:
            state.next_token(scanner, None)
        except Exception as e:
            failed = True
        assert failed is True

        scanner = StringScanner("// Comment \n Comment ")
        token = state.next_token(scanner, None)
        assert "// Comment " == token.value
        assert TokenType.Comment == token.type
