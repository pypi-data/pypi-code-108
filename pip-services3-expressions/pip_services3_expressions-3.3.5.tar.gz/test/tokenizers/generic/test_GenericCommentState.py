# -*- coding: utf-8 -*-

from pip_services3_expressions.io.StringScanner import StringScanner
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.GenericCommentState import GenericCommentState


class TestGenericCommentState:

    def test_next_token(self):
        state = GenericCommentState()

        scanner = StringScanner("# Comment \r# Comment ")
        token = state.next_token(scanner, None)
        assert "# Comment " == token.value
        assert TokenType.Comment == token.type

        scanner = StringScanner("# Comment \n# Comment ")
        token = state.next_token(scanner, None)
        assert "# Comment " == token.value
        assert TokenType.Comment == token.type
