# -*- coding: utf-8 -*-

from pip_services3_expressions.calculator.variables.Variable import Variable
from pip_services3_expressions.calculator.variables.VariableCollection import VariableCollection


class TestVariableCollection:

    def test_add_remove_variables(self):
        collection = VariableCollection()

        var1 = Variable("ABC")
        collection.add(var1)
        assert 1 == collection.length

        var2 = Variable("XYZ")
        collection.add(var2)
        assert 2 == collection.length

        index = collection.find_index_by_name("abc")
        assert 0 == index

        var3 = collection.locate("ghi")
        assert var3 is not None
        assert "ghi" == var3.name
        assert 3 == collection.length

        collection.remove(0)
        assert 2 == collection.length

        collection.remove_by_name('GHI')
        assert 1 == collection.length
