# -*- coding: utf-8 -*-

from pip_services3_expressions.variants.Variant import Variant
from pip_services3_expressions.variants.VariantType import VariantType

from pip_services3_expressions.variants.TypeSafeVariantOperations import TypeSafeVariantOperations


class TestTypeSafeVariantOperations:

    def test_operations(self):
        a = Variant(123)
        manager = TypeSafeVariantOperations()

        b = manager.convert(a, VariantType.Float)
        assert VariantType.Float == b.type
        assert 123.0 == b.as_float

        c = Variant(2)
        assert 125 == manager.add(b, c).as_integer
        assert 121 == manager.sub(b, c).as_integer
        assert manager.equal(a, c).as_boolean is False

        array = [Variant("aaa"), Variant("bbb"), Variant("ccc"), Variant("ddd")]
        d = Variant(array)
        assert manager.in_(d, Variant("ccc")).as_boolean is True
        assert manager.in_(d, Variant("eee")).as_boolean is False
        assert "bbb" == manager.get_element(d, Variant(1)).as_string
