# -*- coding: utf-8 -*-

from pip_services3_expressions.variants.Variant import Variant
from pip_services3_expressions.variants.VariantType import VariantType


class TestVariants:

    def test_variants(self):
        a = Variant(123)
        assert VariantType.Integer == a.type
        assert 123 == a.as_integer
        assert 123 == a.as_object

        b = Variant('xyz')
        assert VariantType.String == b.type
        assert "xyz" == b.as_string
        assert "xyz" == b.as_object
