from e2e.test_variables import TestVars
from rox.server.rox_server import Rox


def create_custom_props():
    Rox.set_custom_string_property('string_prop1', 'Hello')

    def get_custom_string_property(context):
        TestVars.is_computed_string_prop_called = True
        return 'World'

    Rox.set_custom_string_property('string_prop2', get_custom_string_property)

    Rox.set_custom_boolean_property('bool_prop1', True)

    def get_custom_boolean_property(context):
        TestVars.is_computed_boolean_prop_called = True
        return False

    Rox.set_custom_boolean_property('bool_prop2', get_custom_boolean_property)

    Rox.set_custom_int_property('int_prop1', 6)

    def get_custom_int_property(context):
        TestVars.is_computed_int_prop_called = True
        return 28

    Rox.set_custom_int_property('int_prop2', get_custom_int_property)

    Rox.set_custom_float_property('float_prop1', 3.14)

    def get_custom_float_property(context):
        TestVars.is_computed_float_prop_called = True
        return 1.618

    Rox.set_custom_float_property('float_prop2', get_custom_float_property)

    Rox.set_custom_semver_property('smvr_prop1', '9.11.2001')

    def get_custom_semver_property(context):
        TestVars.is_computed_semver_prop_called = True
        return '20.7.1969'

    Rox.set_custom_semver_property('smvr_prop2', get_custom_semver_property)

    Rox.set_custom_boolean_property('bool_prop_target_group_for_variant', lambda context: context['isDuckAndCover'])

    Rox.set_custom_boolean_property('bool_prop_target_group_operand1', lambda context: TestVars.target_group1)

    Rox.set_custom_boolean_property('bool_prop_target_group_operand2', lambda context: TestVars.target_group2)

    Rox.set_custom_boolean_property('bool_prop_target_group_for_dependency', lambda context: TestVars.is_prop_for_target_group_for_dependency)

    Rox.set_custom_boolean_property('bool_prop_target_group_for_variant_dependency', lambda context: context['isDuckAndCover'])
