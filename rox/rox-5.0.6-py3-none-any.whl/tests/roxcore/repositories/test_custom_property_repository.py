import unittest

from rox.core.custom_properties.custom_property import CustomProperty
from rox.core.custom_properties.custom_property_type import CustomPropertyType
from rox.core.repositories.custom_property_repository import CustomPropertyRepository


class CustomPropertyRepositoryTests(unittest.TestCase):
    def test_will_return_null_when_prop_not_found(self):
        repo = CustomPropertyRepository()

        self.assertIsNone(repo.get_custom_property('harti'))

    def test_will_add_prop(self):
        repo = CustomPropertyRepository()
        cp = CustomProperty('prop1', CustomPropertyType.STRING, '123')

        repo.add_custom_property(cp)

        self.assertEqual('prop1', repo.get_custom_property('prop1').name)

    def test_will_not_override_prop(self):
        repo = CustomPropertyRepository()
        cp = CustomProperty('prop1', CustomPropertyType.STRING, '123')
        cp2 = CustomProperty('prop1', CustomPropertyType.STRING, '234')

        repo.add_custom_property_if_not_exists(cp)
        repo.add_custom_property_if_not_exists(cp2)

        self.assertEqual('123', repo.get_custom_property('prop1').value(None))

    def test_will_override_prop(self):
        repo = CustomPropertyRepository()
        cp = CustomProperty('prop1', CustomPropertyType.STRING, '123')
        cp2 = CustomProperty('prop1', CustomPropertyType.STRING, '234')

        repo.add_custom_property_if_not_exists(cp)
        repo.add_custom_property(cp2)

        self.assertEqual('234', repo.get_custom_property('prop1').value(None))

    def test_will_raise_prop_added_event(self):
        repo = CustomPropertyRepository()
        cp = CustomProperty('prop1', CustomPropertyType.STRING, '123')
        prop_from_event = {'prop': None}

        def custom_property_added(custom_property):
            prop_from_event['prop'] = custom_property

        repo.register_custom_property_added_handler(custom_property_added)

        repo.add_custom_property(cp)

        self.assertEqual('prop1', prop_from_event['prop'].name)
