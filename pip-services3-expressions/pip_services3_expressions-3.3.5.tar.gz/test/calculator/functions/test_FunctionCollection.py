# -*- coding: utf-8 -*-

from pip_services3_expressions.calculator.functions.DelegatedFunction import DelegatedFunction
from pip_services3_expressions.calculator.functions.FunctionCollection import FunctionCollection
from pip_services3_expressions.variants.Variant import Variant


class TestFunctionCollection:

    def tst_func(self, params, operations, callback):
        callback(None, Variant("ABC"))

    def test_add_remove_functions(self):
        collection = FunctionCollection()

        func1 = DelegatedFunction("ABC", self.tst_func)
        collection.add(func1)
        assert 1 == collection.length

        func2 = DelegatedFunction("XYZ", self.tst_func)
        collection.add(func2)
        assert 2 == collection.length

        index = collection.find_index_by_name('abc')
        assert 0 == index

        func = collection.find_by_name('Xyz')
        assert func2 == func

        collection.remove(0)
        assert 1 == collection.length

        collection.remove_by_name('XYZ')
        assert 0 == collection.length
