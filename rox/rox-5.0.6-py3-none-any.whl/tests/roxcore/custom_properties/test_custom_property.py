import unittest

from rox.core.custom_properties.custom_property import CustomProperty
from rox.core.custom_properties.custom_property_type import CustomPropertyType
from rox.core.custom_properties.device_property import DeviceProperty


class CustomPropertyTests(unittest.TestCase):
    def test_will_create_property_with_const_value(self):
        prop_string = CustomProperty('prop1', CustomPropertyType.STRING, '123')

        self.assertEqual('prop1', prop_string.name)
        self.assertEqual(CustomPropertyType.STRING, prop_string.type)
        self.assertEqual('123', prop_string.value(None))

        prop_float = CustomProperty('prop1', CustomPropertyType.FLOAT, 123.12)

        self.assertEqual('prop1', prop_float.name)
        self.assertEqual(CustomPropertyType.FLOAT, prop_float.type)
        self.assertEqual(123.12, prop_float.value(None))

        prop_int = CustomProperty('prop1', CustomPropertyType.INT, 123)

        self.assertEqual('prop1', prop_int.name)
        self.assertEqual(CustomPropertyType.INT, prop_int.type)
        self.assertEqual(123, prop_int.value(None))

        prop_bool = CustomProperty('prop1', CustomPropertyType.BOOL, True)

        self.assertEqual('prop1', prop_bool.name)
        self.assertEqual(CustomPropertyType.BOOL, prop_bool.type)
        self.assertEqual(True, prop_bool.value(None))

        prop_semver = CustomProperty('prop1', CustomPropertyType.SEMVER, '1.2.3')

        self.assertEqual('prop1', prop_semver.name)
        self.assertEqual(CustomPropertyType.SEMVER, prop_semver.type)
        self.assertEqual('1.2.3', prop_semver.value(None))

    def test_will_create_property_with_func_value(self):
        prop_string = CustomProperty('prop1', CustomPropertyType.STRING, lambda c: '123')

        self.assertEqual('prop1', prop_string.name)
        self.assertEqual(CustomPropertyType.STRING, prop_string.type)
        self.assertEqual('123', prop_string.value(None))

        prop_float = CustomProperty('prop1', CustomPropertyType.FLOAT, lambda c: 123.12)

        self.assertEqual('prop1', prop_float.name)
        self.assertEqual(CustomPropertyType.FLOAT, prop_float.type)
        self.assertEqual(123.12, prop_float.value(None))

        prop_int = CustomProperty('prop1', CustomPropertyType.INT, lambda c: 123)

        self.assertEqual('prop1', prop_int.name)
        self.assertEqual(CustomPropertyType.INT, prop_int.type)
        self.assertEqual(123, prop_int.value(None))

        prop_bool = CustomProperty('prop1', CustomPropertyType.BOOL, lambda c: True)

        self.assertEqual('prop1', prop_bool.name)
        self.assertEqual(CustomPropertyType.BOOL, prop_bool.type)
        self.assertEqual(True, prop_bool.value(None))

        prop_semver = CustomProperty('prop1', CustomPropertyType.SEMVER, lambda c: '1.2.3')

        self.assertEqual('prop1', prop_semver.name)
        self.assertEqual(CustomPropertyType.SEMVER, prop_semver.type)
        self.assertEqual('1.2.3', prop_semver.value(None))

    def test_will_pass_context(self):
        context = {'a': 1}

        context_from_func = {'context': None}

        def get_prop_value(context):
            context_from_func['context'] = context
            return '123'

        prop_string = CustomProperty('prop1', CustomPropertyType.STRING, get_prop_value)

        self.assertEqual('123', prop_string.value(context))
        self.assertEqual(1, context_from_func['context'].get('a'))

    def test_device_prop_wil_add_rox_to_the_name(self):
        prop = DeviceProperty('prop1', CustomPropertyType.STRING, '123')

        self.assertEqual('rox.prop1', prop.name)

