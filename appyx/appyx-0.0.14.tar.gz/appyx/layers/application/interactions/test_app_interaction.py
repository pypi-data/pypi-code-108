from appyx.layers.application.interactions.app_interaction import AppInteraction
from appyx.layers.application.interactions.parameters.parameter import Parameter
from appyx.layers.application.interactions.parameters.test_command_parameters import TestApp
from appyx.layers.application.interactions.proto_interaction_test import AppyxTest
from appyx.layers.domain.messages.exceptions import DuplicateParameterException


class AppInteractionTest(AppyxTest.ProtoInteractionTest):
    """
    Tests the behavior of the abstract class AppInteraction (ex AppCommand)
    Note: These tests should be split in two:
        1 - Tests that validate appyx behavior
        2 - Tests that are inheritable and that are run on concrete subclasses
    """

    def _new_sample_proto_interaction(self):
        return self.app_command()

    def test_a_new_interaction_doesnt_have_parameters(self):
        # Given a new interaction
        cmd = self.app_command()

        # When we ask for its parameters
        parameters = cmd.get_parameters()

        # Then an empty list is returned
        self.assertEqual(parameters.size(), 0)

    def app(self):
        return TestApp()

    def app_command(self):
        return AppInteraction(app=self.app())

    def test_a_new_interaction_can_have_added_a_new_parameter(self):
        # Given a new interaction
        cmd = self.app_command()

        # When we add a new parameter
        parameter_price = Parameter(u"price", [])
        cmd.add_parameter(parameter_price)

        # Then we can retrieve it in various ways
        parameters = cmd.get_parameters()
        self.assertEqual(parameters.size(), 1)
        self.assertEqual(parameter_price, cmd.get_parameter_named(u"price"))

    def test_setting_parameters_erases_the_previous_ones(self):
        # Given a new interaction with three parameters
        cmd = self.app_command()
        cmd.add_parameters([Parameter(u"price", []), Parameter(u"currency", []), Parameter(u"is_cash", [])])
        self.assertEqual(cmd.get_parameters().size(), 3)

        # When we add a set parameters
        parameter_price = Parameter(u"price", [])
        cmd.set_parameters([parameter_price])

        # Then the amount of parameters is 1
        parameters = cmd.get_parameters()
        self.assertEqual(parameters.size(), 1)
        self.assertEqual(parameter_price, cmd.get_parameter_named(u"price"))

    def test_an_interaction_cannot_have_two_parameters_with_the_same_name(self):
        # Given an interaction with one parameter
        cmd = self.app_command()
        parameter_price = Parameter(u"price", [])
        cmd.add_parameter(parameter_price)

        # When we add a new parameter
        parameter_price = Parameter(u"price", [])
        exception = None
        try:
            cmd.add_parameter(parameter_price)
        except DuplicateParameterException as error:
            exception = error

        # Then an error occurred
        self.assertEqual("Parameter price is already present", str(exception))

    def test_an_interaction_cannot_have_a_parameter_named_none(self):
        # Given an interaction with one parameter
        cmd = self.app_command()

        # When we add a new parameter
        # noinspection PyTypeChecker
        parameter_precio = Parameter(None, [])
        exception = None
        try:
            cmd.add_parameter(parameter_precio)
        except ValueError as error:
            exception = error

        # Then an error occurred
        self.assertIsNotNone(exception)

    def test_an_interaction_cannot_have_a_parameter_named_empty_string(self):
        # Given an interaction with one parameter
        cmd = self.app_command()

        # When we add a new parameter
        parameter_precio = Parameter('', [])

        # Then an error occurred
        self.assertRaises(ValueError, cmd.add_parameter, parameter_precio)

    def test_an_interaction_cannot_have_a_parameter_named_empty_unicode_string(self):
        # Given an interaction with one parameter
        cmd = self.app_command()

        # When we add a new parameter
        parameter_precio = Parameter(u"", [])
        exception = None
        try:
            cmd.add_parameter(parameter_precio)
        except ValueError as error:
            exception = error

        # Then an error occurred
        self.assertIsNotNone(exception)

    def test_a_parameter_with_no_validators_is_valid(self):
        # Given an interaction with a parameter without validators
        cmd = self.app_command()
        parameter = Parameter(u"nombre", [])
        cmd.add_parameter(parameter)

        # When we ask can_execute
        result = cmd.validate()

        # Then the result is successful
        self.assertTrue(result.is_successful())

    def test_a_parameter_can_be_defined_as_required(self):
        # Given an interaction with a parameter
        cmd = self.app_command()
        parameter = Parameter(u"name", [])
        cmd.add_parameter(parameter)

        # When we set it as required
        cmd.add_required_parameter_named(u"name")

        # Then it's name appears in the required parameters list
        self.assertIn(u"name", cmd.required_parameter_names())

    def test_a_required_parameter_with_an_argument_is_valid(self):
        # Given an interaction with a required parameter
        cmd = self.app_command()
        parameter = Parameter(u"name", [])
        cmd.add_parameter(parameter)
        cmd.add_required_parameter_named(u"name")
        # and a corresponding argument
        cmd.set_arguments({u"name": "Eustaquio"})

        # When we ask can_execute
        result = cmd.validate()

        # Then the result is successful
        self.assertTrue(result.is_successful())

    def test_a_required_parameter_with_no_arguments_is_invalid(self):
        # Given an interaction with a parameter without validators
        cmd = self.app_command()
        parameter = Parameter(u"name", [])
        cmd.add_parameter(parameter)
        cmd.add_required_parameter_named(u"name")

        # When we ask can_execute
        result = cmd.validate()

        # Then the result is not successful
        self.assertTrue(result.has_errors())
        self.assertTrue(result.has_error_with_code("parameter_missing_error"))

    def test_a_required_parameter_can_be_made_optional(self):
        # Given an interaction with a required parameter and no argument for it
        cmd = self.app_command()
        parameter = Parameter(u"name", [])
        cmd.add_parameter(parameter)
        cmd.add_required_parameter_named(u"name")

        # When we make it optional
        cmd.remove_required_parameter_named(u"name")

        # Then the interaction is valid
        result = cmd.validate()
        self.assertTrue(result.is_successful())

    def test_a_parameter_can_be_declared_as_required_twice(self):
        # Given an interactionwith a required parameter
        cmd = self.app_command()
        parameter = Parameter(u"name", [])
        cmd.add_parameter(parameter)
        cmd.add_required_parameter_named(u"name")
        cmd.add_required_parameter_named(u"name")
        # and a corresponding argument
        cmd.set_arguments({u"name": "Eustaquio"})

        # When we ask can_execute
        result = cmd.validate()

        # Then the result is successful
        self.assertTrue(result.is_successful())

    def test_a_parameter_declared_twice_as_required_can_be_made_optional(self):
        # Given an interactionwith double required parameter and no argument for it
        cmd = self.app_command()
        parameter = Parameter(u"nombre", [])
        cmd.add_parameter(parameter)
        cmd.add_required_parameter_named(u"nombre")
        cmd.add_required_parameter_named(u"nombre")

        # When we make it optional
        cmd.remove_required_parameter_named(u"nombre")

        # Then the interaction is valid
        result = cmd.validate()
        self.assertTrue(result.is_successful())

    def test_an_interaction_can_have_one_of_three_parameters_required(self):
        # Given an interaction with three parameters
        cmd = self.app_command()
        parameter1 = Parameter(u"telefono", [])
        parameter2 = Parameter(u"mail", [])
        parameter3 = Parameter(u"whatsapp", [])
        cmd.add_parameter(parameter1)
        cmd.add_parameter(parameter2)
        cmd.add_parameter(parameter3)

        # When we set one as required and define one of them
        cmd.add_at_least_one_constraint([u"telefono", u"mail", u"whatsapp"])
        cmd.set_arguments({u"mail": 'test@probado.com'})

        # Then it should be ready to execute
        result = cmd.validate()
        self.assertTrue(result.is_successful())

    def test_an_interaction_must_have_one_of_three_parameters_required_defined(self):
        # Given an interaction with three parameters
        cmd = self.app_command()
        parameter1 = Parameter(u"telefono", [])
        parameter2 = Parameter(u"mail", [])
        parameter3 = Parameter(u"whatsapp", [])
        cmd.add_parameter(parameter1)
        cmd.add_parameter(parameter2)
        cmd.add_parameter(parameter3)

        # When we set one as required and don't define any of them
        cmd.add_at_least_one_constraint([u"telefono", u"mail", u"whatsapp"])

        # Then it should NOT be ready to execute
        result = cmd.validate()
        self.assertTrue(not result.is_successful())

    def test_interaction_parameters_can_be_set_and_read_individually(self):
        # Given an interaction with one parameter
        cmd = self.app_command()
        parameter = Parameter(u"nombre", [])
        cmd.add_parameter(parameter)

        # When we set the parameter argument
        cmd.set_argument_value(u"nombre", "Pepe Glamour")

        # Then we can retrieve it
        value = cmd.get_argument_named(u"nombre")
        self.assertEqual("Pepe Glamour", value)
