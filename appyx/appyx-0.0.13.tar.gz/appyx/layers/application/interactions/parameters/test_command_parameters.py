from unittest import TestCase

from appyx.layers.application.application import Application
from appyx.layers.application.interactions.app_interaction import AppInteraction
from appyx.layers.application.interactions.parameters.parameter import Parameter
from appyx.layers.domain.messages.exceptions import ArgumentNotFound, DuplicateParameterException


class TestApp(Application):
    def default_running_context(self):
        return 'SARASA'


class CommandParametersTest(TestCase):
    def setUp(self) -> None:
        self._app = TestApp()

    def test_a_new_command_doesnt_have_parameters(self):
        # Given a new command
        cmd = AppInteraction(self._app)

        # When we ask for its parameters
        parameters = cmd.get_parameters()

        # Then an empty list is returned
        self.assertEqual(parameters.size(), 0)

    def test_a_new_command_can_have_added_a_new_parameter(self):
        # Given a new command
        cmd = AppInteraction(self._app)

        # When we add a new parameter
        parameter_precio = Parameter(u"precio", [])
        cmd.add_parameter(parameter_precio)

        # Then we can retrieve it in various ways
        parameters = cmd.get_parameters()
        self.assertEqual(parameters.size(), 1)
        self.assertEqual(parameter_precio, cmd.get_parameter_named(u"precio"))

    def test_setting_parameters_erases_the_previous_ones(self):
        # Given a new command with three parameters
        cmd = AppInteraction(self._app)
        cmd.add_parameters([Parameter(u"precio", []), Parameter(u"moneda", []), Parameter(u"es_contado", [])])
        self.assertEqual(cmd.get_parameters().size(), 3)

        # When we add a set parameters
        parameter_price = Parameter(u"price", [])
        cmd.set_parameters([parameter_price])

        # Then the amount of parameters is 1
        parameters = cmd.get_parameters()
        self.assertEqual(parameters.size(), 1)
        self.assertEqual(parameter_price, cmd.get_parameter_named(u"price"))

    def test_a_command_cannot_have_two_parameters_with_the_same_name(self):
        # Given a command with one parameter
        cmd = AppInteraction(self._app)
        parameter_precio = Parameter(u"precio", [])
        cmd.add_parameter(parameter_precio)

        # When we add a new parameter
        parameter_precio = Parameter(u"precio", [])
        exception = None
        try:
            cmd.add_parameter(parameter_precio)
        except DuplicateParameterException as error:
            exception = error

        # Then an error occurred
        self.assertEqual("Parameter precio is already present", str(exception))

    def test_a_command_cannot_have_a_parameter_named_none(self):
        # Given a command with one parameter
        cmd = AppInteraction(self._app)

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

    def test_a_command_cannot_have_a_parameter_named_empty_string(self):
        # Given a command with one parameter
        cmd = AppInteraction(self._app)

        # When we add a new parameter
        parameter_precio = Parameter('', [])

        # Then an error occurred
        self.assertRaises(ValueError, cmd.add_parameter, parameter_precio)

    def test_a_command_cannot_have_a_parameter_named_empty_unicode_string(self):
        # Given a command with one parameter
        cmd = AppInteraction(self._app)

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
        # Given a command with a parameter without validators
        cmd = AppInteraction(self._app)
        parameter = Parameter(u"nombre", [])
        cmd.add_parameter(parameter)

        # When we ask can_execute
        result = cmd.can_execute()

        # Then the result is successful
        self.assertTrue(result.is_successful())

    def test_a_parameter_can_be_defined_as_required(self):
        # Given a command with a parameter
        cmd = AppInteraction(self._app)
        parameter = Parameter(u"nombre", [])
        cmd.add_parameter(parameter)

        # When we set it as required
        cmd.add_required_parameter_named(u"nombre")

        # Then it's name appears in the required parameters list
        self.assertIn(u"nombre", cmd.required_parameter_names())

    def test_a_required_parameter_with_an_argument_is_valid(self):
        # Given a command with a required parameter
        cmd = AppInteraction(self._app)
        parameter = Parameter(u"nombre", [])
        cmd.add_parameter(parameter)
        cmd.add_required_parameter_named(u"nombre")
        # and a corresponding argument
        cmd.set_arguments({u"nombre": "Eustaquio"})

        # When we ask can_execute
        result = cmd.can_execute()

        # Then the result is successful
        self.assertTrue(result.is_successful())

    def test_a_required_parameter_with_no_arguments_is_invalid(self):
        # Given a command with a parameter without validators
        cmd = AppInteraction(self._app)
        parameter = Parameter(u"nombre", [])
        cmd.add_parameter(parameter)
        cmd.add_required_parameter_named(u"nombre")

        # When we ask can_execute
        result = cmd.can_execute()

        # Then the result is not successful
        self.assertTrue(result.has_errors())
        self.assertEqual(len(result.errors()), 1)
        self.assertEqual(result.errors()[0].code(), "parameter_missing_error")

    def test_a_required_parameter_can_be_made_optional(self):
        # Given a command with a required parameter and no argument for it
        cmd = AppInteraction(self._app)
        parameter = Parameter(u"nombre", [])
        cmd.add_parameter(parameter)
        cmd.add_required_parameter_named(u"nombre")

        # When we make it optional
        cmd.remove_required_parameter_named(u"nombre")

        # Then the command can execute
        result = cmd.can_execute()
        self.assertTrue(result.is_successful())

    def test_a_parameter_can_be_declared_as_required_twice(self):
        # Given a command with a required parameter
        cmd = AppInteraction(self._app)
        parameter = Parameter(u"nombre", [])
        cmd.add_parameter(parameter)
        cmd.add_required_parameter_named(u"nombre")
        cmd.add_required_parameter_named(u"nombre")
        # and a corresponding argument
        cmd.set_arguments({u"nombre": "Eustaquio"})

        # When we ask can_execute
        result = cmd.can_execute()

        # Then the result is successful
        self.assertTrue(result.is_successful())

    def test_a_parameter_declared_twice_as_required_can_be_made_optional(self):
        # Given a command with double required parameter and no argument for it
        cmd = AppInteraction(self._app)
        parameter = Parameter(u"nombre", [])
        cmd.add_parameter(parameter)
        cmd.add_required_parameter_named(u"nombre")
        cmd.add_required_parameter_named(u"nombre")

        # When we make it optional
        cmd.remove_required_parameter_named(u"nombre")

        # Then the command can execute
        result = cmd.can_execute()
        self.assertTrue(result.is_successful())

    def test_a_command_can_have_one_of_three_parameters_required(self):
        # Given a command with three parameters
        cmd = AppInteraction(self._app)
        parameter1 = Parameter(u"phone", [])
        parameter2 = Parameter(u"mail", [])
        parameter3 = Parameter(u"whatsapp", [])
        cmd.add_parameter(parameter1)
        cmd.add_parameter(parameter2)
        cmd.add_parameter(parameter3)

        # When we set one as required and define one of them
        cmd.add_at_least_one_constraint([u"phone", u"mail", u"whatsapp"])
        cmd.set_arguments({u"mail": 'test@probado.com'})

        # Then it should be ready to execute
        result = cmd.can_execute()
        self.assertTrue(result.is_successful())

    def test_a_command_must_have_one_of_three_parameters_required_defined(self):
        # Given a command with three parameters
        cmd = AppInteraction(self._app)
        parameter1 = Parameter(u"phone", [])
        parameter2 = Parameter(u"mail", [])
        parameter3 = Parameter(u"whatsapp", [])
        cmd.add_parameter(parameter1)
        cmd.add_parameter(parameter2)
        cmd.add_parameter(parameter3)

        # When we set one as required and don't define any of them
        cmd.add_at_least_one_constraint([u"phone", u"mail", u"whatsapp"])

        # Then it should NOT be ready to execute
        result = cmd.can_execute()
        self.assertTrue(not result.is_successful())

    def test_command_parameters_can_be_set_and_read_individually(self):
        # Given a command with one parameter
        cmd = AppInteraction(self._app)
        parameter = Parameter(u"nombre", [])
        cmd.add_parameter(parameter)

        # When we set the parameter argument
        cmd.set_argument_value(u"nombre", "Pepe Glamour")

        # Then we can retrieve it
        value = cmd.get_argument_named(u"nombre")
        self.assertEqual("Pepe Glamour", value)

    def test_when_asked_for_a_missing_parameter_None_is_returned(self):
        # Given an interaction with a declared parameter
        cmd = AppInteraction(self._app)
        parameter = Parameter(u"nombre", [])
        cmd.add_parameter(parameter)
        cmd.add_required_parameter_named(u"nombre")
        cmd.set_arguments({'nombre': 'Julian'})

        # When we ask for a parameter that is not declared
        parameter_asked = cmd.get_parameter_named("apellido")

        # Then a particular exception is raised
        self.assertIsNone(parameter_asked)

    def test_when_asked_for_a_missing_argument_an_exception_is_raised(self):
        # Given an interaction with a declared parameter
        cmd = AppInteraction(self._app)
        parameter = Parameter(u"nombre", [])
        cmd.add_parameter(parameter)
        cmd.add_required_parameter_named(u"nombre")
        cmd.set_arguments({'nombre': 'Julian'})
        exception_raised = None

        # When we ask for an argument that has no parameter
        try:
            cmd.get_argument_named("apellido")
        except ArgumentNotFound as error:
            exception_raised = error

        # Then a particular exception is raised
        self.assertEqual('Argument named: apellido not found', str(exception_raised))
