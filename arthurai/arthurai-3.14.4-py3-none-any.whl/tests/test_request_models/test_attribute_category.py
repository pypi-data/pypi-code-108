from arthurai.core.attributes import AttributeCategory


class TestAttributeCategory:

    def test_value_type(self):
        for val, label in [(1, 1), ("1", 1), (1, "1"), (1.0, 1.0), (1, None)]:
            ac = AttributeCategory(value=val, label=label)
            assert isinstance(ac.value, str)
            if ac.label is not None:
                assert isinstance(ac.label, str)
