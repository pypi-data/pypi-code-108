# -*- coding: utf-8 -*-

from pip_services3_expressions.calculator.parsers.ExpressionParser import ExpressionParser
from pip_services3_expressions.calculator.parsers.ExpressionToken import ExpressionToken
from pip_services3_expressions.calculator.parsers.ExpressionTokenType import ExpressionTokenType
from pip_services3_expressions.variants.Variant import Variant


class TestExpressionParser:
    def test_parse_string(self):
        parser = ExpressionParser()
        parser.expression = "(2+2)*ABS(-2)"
        expected_tokens = [
            ExpressionToken(ExpressionTokenType.Constant, Variant.from_integer(2), 0, 0),
            ExpressionToken(ExpressionTokenType.Constant, Variant.from_integer(2), 0, 0),
            ExpressionToken(ExpressionTokenType.Plus, Variant.Empty(), 0, 0),
            ExpressionToken(ExpressionTokenType.Constant, Variant.from_integer(2), 0, 0),
            ExpressionToken(ExpressionTokenType.Unary, Variant.Empty(), 0, 0),
            ExpressionToken(ExpressionTokenType.Constant, Variant.from_integer(1), 0, 0),
            ExpressionToken(ExpressionTokenType.Function, Variant.from_string("ABS"), 0, 0),
            ExpressionToken(ExpressionTokenType.Star, Variant.Empty(), 0, 0),
        ]
        tokens = parser.result_tokens
        assert len(expected_tokens) == len(tokens)

        for i in range(len(tokens)):
            assert expected_tokens[i].type == tokens[i].type
            assert expected_tokens[i].value.type == tokens[i].value.type
            assert expected_tokens[i].value.as_object == tokens[i].value.as_object

    def test_wrong_expression(self):
        parser = ExpressionParser()
        parser.expression = "1 > 2"
        assert '1 > 2' == parser.expression
