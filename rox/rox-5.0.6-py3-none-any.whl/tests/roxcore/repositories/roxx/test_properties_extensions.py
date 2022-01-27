import unittest

from rox.core.custom_properties.custom_property import CustomProperty
from rox.core.custom_properties.custom_property_type import CustomPropertyType
from rox.core.repositories.custom_property_repository import CustomPropertyRepository
from rox.core.repositories.roxx.properties_extensions import PropertiesExtensions
from rox.core.error_handling.exception_trigger import ExceptionTrigger
from rox.core.roxx.parser import Parser

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

# A custom property resolver that always raises an exception
propertyResolverException = Exception('exception from property resolver')
def brokenPropertyResolver(context):
    raise propertyResolverException

class PropertiesExtensionsTests(unittest.TestCase):

    def test_roxx_properties_extensions_string(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser(None)

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('testKey', CustomPropertyType.STRING, 'test'))

        self.assertEqual(True, parser.evaluate_expression('eq("test", property("testKey"))').value)

    def test_roxx_properties_extensions_int(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser(None)

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('testKey', CustomPropertyType.INT, 3))

        self.assertEqual(True, parser.evaluate_expression('eq(3, property("testKey"))').value)

    def test_roxx_properties_extensions_float(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser(None)

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('testKey', CustomPropertyType.FLOAT, 3.3))

        self.assertEqual(True, parser.evaluate_expression('eq(3.3, property("testKey"))').value)

    def test_roxx_properties_extensions_with_context_string(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser(None)

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('CustomPropertyTestKey', CustomPropertyType.STRING,
                                                                      lambda c: c.get('ContextTestKey')))
        context = {'ContextTestKey': 'test'}

        self.assertEqual(True, parser.evaluate_expression('eq("test", property("CustomPropertyTestKey"))', context).value)

    def test_roxx_properties_extensions_with_context_int(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser(None)

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('CustomPropertyTestKey', CustomPropertyType.INT,
                                                                      lambda c: c.get('ContextTestKey')))
        context = {'ContextTestKey': 3}

        self.assertEqual(True, parser.evaluate_expression('eq(3, property("CustomPropertyTestKey"))', context).value)

    def test_roxx_properties_extensions_with_context_int_with_string(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser(None)

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('CustomPropertyTestKey', CustomPropertyType.INT,
                                                                      lambda c: c.get('ContextTestKey')))
        context = {'ContextTestKey': 3}

        self.assertEqual(False, parser.evaluate_expression('eq("3", property("CustomPropertyTestKey"))', context).value)

    def test_roxx_properties_extensions_with_context_int_not_equal(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser(None)

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('CustomPropertyTestKey', CustomPropertyType.INT,
                                                                      lambda c: c.get('ContextTestKey')))
        context = {'ContextTestKey': 3}

        self.assertEqual(False, parser.evaluate_expression('eq(4, property("CustomPropertyTestKey"))', context).value)

    def test_unknown_property(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser(None)

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('testKey', CustomPropertyType.STRING, 'test'))

        self.assertEqual(False, parser.evaluate_expression('eq("test", property("testKey1"))').value)

    def test_null_property(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser(None)

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('testKey', CustomPropertyType.STRING,
                                                                      lambda c: None))

        self.assertEqual(True, parser.evaluate_expression('eq(undefined, property("testKey"))').value)

    def test_dynamic_properties_handler(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser(None)

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository, lambda prop_name, context: context[prop_name])
        roxx_properties_extensions.extend()

        condition = 'property("not_here")'
        result = parser.evaluate_expression(condition, { 'not_here': 'stam' }).value
        self.assertEqual('stam', result)

    def test_dynamic_properties_handler_throws_error(self):
        custom_property_repository = CustomPropertyRepository()
        unhandledErrorHandler = Mock()
        parser = Parser(unhandledErrorHandler)

        custom_property_repository.add_custom_property(CustomProperty('customprop1', CustomPropertyType.STRING, brokenPropertyResolver))

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository, lambda prop_name, context: context[prop_name])
        roxx_properties_extensions.extend()

        condition = 'property("customprop1")'
        result = parser.evaluate_expression(condition, { 'customprop1': 'true' }).value

        # Check that our custom property resolver function is identified as the cause of the error:
        unhandledErrorHandler.invoke.assert_called_once_with(
            brokenPropertyResolver,
            ExceptionTrigger.CUSTOM_PROPERTY_GENERATOR,
            propertyResolverException)

        self.assertIsNone(result)
