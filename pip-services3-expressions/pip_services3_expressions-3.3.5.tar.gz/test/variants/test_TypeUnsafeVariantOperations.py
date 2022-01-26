# -*- coding: utf-8 -*-

from pip_services3_expressions.variants.Variant import Variant
from pip_services3_expressions.variants.VariantType import VariantType

from pip_services3_expressions.variants.TypeUnsafeVariantOperations import TypeUnsafeVariantOperations


class TestTypeUnsafeVariantOperations:

    def test_operations(self):
        a = Variant("123")
        manager = TypeUnsafeVariantOperations()

        b = manager.convert(a, VariantType.Float)
        assert VariantType.Float == b.type
        assert 123.0 == b.as_float

        c = Variant(2)
        assert 125.0 == manager.add(b, c).as_float
        assert 121.0 == manager.sub(b, c).as_float
        assert manager.equal(a, b).as_boolean is True
