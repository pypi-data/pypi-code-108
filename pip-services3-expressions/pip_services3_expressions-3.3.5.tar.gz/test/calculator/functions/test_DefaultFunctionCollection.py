# -*- coding: utf-8 -*-
import datetime

from pip_services3_commons.convert import StringConverter

from pip_services3_expressions.calculator.functions.DefaultFunctionCollection import DefaultFunctionCollection
from pip_services3_expressions.variants.TypeUnsafeVariantOperations import TypeUnsafeVariantOperations
from pip_services3_expressions.variants.Variant import Variant
from pip_services3_expressions.variants.VariantType import VariantType


class TestDefaultFunctionCollection:

    def tst_func(self, params, operations, callback):
        callback(None, Variant("ABC"))

    def test_calculate_functions(self):
        collection = DefaultFunctionCollection()
        params = [
            Variant(1),
            Variant(2),
            Variant(3)
        ]
        operations = TypeUnsafeVariantOperations()

        func = collection.find_by_name("sum")
        assert func is not None

        result = func.calculate(params, operations)
        assert VariantType.Integer == result.type
        assert 6 == result.as_integer

    def test_date_functions(self):
        collection = DefaultFunctionCollection()
        params = []
        operations = TypeUnsafeVariantOperations()

        func = collection.find_by_name("now")
        assert func is not None

        result = func.calculate(params, operations)
        assert VariantType.DateTime == result.type

        collection = DefaultFunctionCollection()
        params = [
            Variant(1975),
            Variant(4),
            Variant(8)
        ]
        operations = TypeUnsafeVariantOperations()

        func = collection.find_by_name("date")
        assert func is not None

        result = func.calculate(params, operations)
        assert VariantType.DateTime == result.type
        assert StringConverter.to_string(datetime.datetime(1975, 3, 8)) == StringConverter.to_string(result.as_datetime)
