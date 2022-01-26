# -*- coding: utf-8 -*-

import pytest

from pip_services3_expressions.calculator.ExpressionCalculator import ExpressionCalculator
from pip_services3_expressions.calculator.ExpressionException import ExpressionException
from pip_services3_expressions.variants.Variant import Variant
from pip_services3_expressions.variants.VariantType import VariantType


class TestExpressionCalculator:

    def test_simple_expression(self):
        calculator = ExpressionCalculator()
        calculator.expression = "2 + 2"
        result = calculator.evaluate()
        assert result is not None
        assert VariantType.Integer == result.type
        assert 4 == result.as_integer

    def test_function_expression(self):
        calculator = ExpressionCalculator()
        calculator.expression = "A + b / (3 - Max(-123, 1)*2)"

        assert 'A' == calculator.default_variables.find_by_name('a').name
        assert 'b' == calculator.default_variables.find_by_name('b').name
        calculator.default_variables.find_by_name('a').value = Variant('xyz')
        calculator.default_variables.find_by_name('b').value = Variant(123)

        result = calculator.evaluate()
        assert result is not None
        assert VariantType.String == result.type
        assert 'xyz123' == result.as_string

    def test_array_expressions(self):
        calculator = ExpressionCalculator()

        calculator.expression = "'abc'[1]"
        result = calculator.evaluate()
        assert result is not None
        assert VariantType.String == result.type
        assert "b" == result.as_string

    def test_boolean_expression(self):
        calculator = ExpressionCalculator()
        calculator.expression = "1 > 2"
        result = calculator.evaluate()
        assert result is not None
        assert VariantType.Boolean == result.type
        assert result.as_boolean is False

    def test_unknown_function(self):
        calculator = ExpressionCalculator()
        with pytest.raises(ExpressionException):
            calculator.expression = "XXX(1)"
            result = calculator.evaluate()
            assert result is None

    def test_in_expression(self):
        calculator = ExpressionCalculator()
        calculator.expression = "2 IN ARRAY(1,2,3)"
        result = calculator.evaluate()
        assert result is not None
        assert VariantType.Boolean == result.type
        assert result.as_boolean is True

        calculator = ExpressionCalculator()
        calculator.expression = "5 NOT IN ARRAY(1,2,3)"
        result = calculator.evaluate()
        assert result is not None
        assert VariantType.Boolean == result.type
        assert result.as_boolean is True
