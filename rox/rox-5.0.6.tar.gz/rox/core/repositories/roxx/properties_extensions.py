from rox.core.roxx.token_type import TokenTypes
from rox.core.error_handling.userspace_handler_exception import UserspaceHandlerException
from rox.core.error_handling.exception_trigger import ExceptionTrigger


class PropertiesExtensions:
    def __init__(self, parser, properties_repository, dynamic_properties_handler=None):
        self.parser = parser
        self.properties_repository = properties_repository
        self.dynamic_properties_handler = dynamic_properties_handler

    def extend(self):
        self.parser.add_operator('property', lambda parser, stack, context: property(self.properties_repository, parser, stack, context, self.dynamic_properties_handler))


def property(properties_repository, parser, stack, context, dynamic_properties_handler):
    prop_name = str(stack.pop())
    property = properties_repository.get_custom_property(prop_name)
    handler = dynamic_properties_handler if dynamic_properties_handler is not None else None

    if property is None:
        if handler is None:
            stack.push(TokenTypes.UNDEFINED)
            return
        try:
            value = handler(prop_name, context)
            stack.push(TokenTypes.UNDEFINED if value is None else value)
            return
        except Exception as ex:
            raise UserspaceHandlerException(handler, ExceptionTrigger.DYNAMIC_PROPERTIES_RULE, ex)

    try:
        value = property.value(context)
        stack.push(TokenTypes.UNDEFINED if value is None else value)
    except Exception as ex:
        raise UserspaceHandlerException(property.value, ExceptionTrigger.CUSTOM_PROPERTY_GENERATOR, ex)

