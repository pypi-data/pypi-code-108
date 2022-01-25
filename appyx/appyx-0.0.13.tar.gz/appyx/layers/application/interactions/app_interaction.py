from appyx.layers.application.interactions.interaction import Interaction
from appyx.layers.application.interactions.parameters.interaction_parameters import InteractionParameters
from appyx.layers.domain.exceptions.early_return import EarlyReturnBecauseOfErrorsException
from appyx.layers.domain.result import Result


class AppInteraction(Interaction):
    """
    I model an interaction in the context of an Application.
    I usually model also the operation that is being performed.
    """

    def __init__(self, app):
        super().__init__()
        self._app = app
        self._parameters = InteractionParameters(self,
                                                 self._initial_parameters(),
                                                 self._initial_required_parameter_names(),
                                                 self._initial_at_least_one_required_sets(),
                                                 self._default_arguments())

    def app(self):
        return self._app

    def set_arguments(self, arguments):
        """
        Set the values that each parameter will have.
        Arguments is a dictionary with the names of the parameters as keys and the value of the argument as value.

        :param arguments: dict of str: object
        """
        self._parameters.set_arguments(arguments)

    def set_keyword_arguments(self, **arguments):
        """
        Set the values that each parameter will have.
        Arguments are keyword arguments.
        """
        # TODO: @laski thinks this should be the only way to set arguments.
        # Compare:
        #     command.set_arguments({command.PARAMETER_KEY_USER: buenbit_user})
        # with
        #     command.set_arguments(user=buenbit_user)
        # The latter is clearer, easier to remember and delegates to Python the validation of the arguments.
        # Also, using string as argument values is error
        self.set_arguments(arguments)

    def can_execute(self):
        """
        Answers the result of trying to execute.

        If result has no errors, it means the command can be executed (although it may fail if further problems arise).
        If result has errors, then the command can not be executed (and the errors explain why)
        """
        result = Result()
        try:
            result = self._validate_parameters_and_arguments(result)
            return result
        except Exception as exc:
            exception_handler = self.app().general_exception_handler()
            result = exception_handler.handle(exc, result)
            return result

    def validate(self):
        return self.can_execute()

    def execute(self):
        """
        Performs the operation of the receiver and answers the result of the execution.

        :return: result of execution
        """
        result = self.can_execute()
        try:
            if result.has_errors():
                return result
            return self._execute_from_successful_parameter_validation(result)
        except EarlyReturnBecauseOfErrorsException:
            return result
        except Exception as exc:
            exception_handler = self.app().general_exception_handler()
            result = exception_handler.handle(exc, result)
            return result

    def execute_with(self, **kwargs):
        """
        Syntax sugar to simplify command execution with a list of arguments
        Replaces boilerplate constructions like this:
            arguments = {ValidateUserSafetyCommand.PARAMETER_KEY_USER: buenbit_user}
            command.set_arguments(arguments)
            result = command.execute()
        with:
            result = command.execute_with(user=buenbit_user)
        """
        self.set_arguments(kwargs)
        result = self.execute()
        return result

    def get_parameters(self):
        return self._parameters

    def add_parameter(self, parameter):
        self._parameters.add_parameter(parameter)

    def set_parameters(self, parameters):
        self._parameters.clear_parameters()
        self.add_parameters(parameters)

    def add_parameters(self, parameters):
        for parameter in parameters:
            self.add_parameter(parameter)

    def set_argument_value(self, argument_name, value):
        return self.get_parameters().set_argument_value(argument_name, value)

    def is_defined_argument_named(self, argument_name):
        return self.get_parameters().is_defined_argument_named(argument_name)

    def get_argument_named(self, argument_name):
        return self.get_parameters().get_argument_named(argument_name)

    def get_parameter_named(self, name):
        return self._parameters.get_parameter_named(name)

    def add_parameters_validator(self, parameters_validator):
        self._parameters.add_parameters_validator(parameters_validator)

    def add_required_parameter_named(self, parameter_name):
        self._parameters.add_required_parameter_named(parameter_name)

    def remove_required_parameter_named(self, parameter_name):
        self._parameters.remove_required_parameter_named(parameter_name)

    def required_parameter_names(self):
        return self._parameters.required_parameter_names()

    def add_at_least_one_constraint(self, parameter_names):
        self._parameters.add_at_least_one_constraint(parameter_names)

    def add_at_least_one_not_none_constraint(self, parameter_names):
        self._parameters.add_at_least_one_not_none_constraint(parameter_names)

    def handle_unexpected_arguments(self, extra_arguments, result):
        """Handle the existence of more arguments than those supported by parameters.

        Note: Currently, we don't raise warnings or errors for this case.
        If you want to do something about extra arguments, override this method.

        :param extra_arguments: the names of the arguments that has no matching parameter
        :param result: result object in which to add the error or warning about this issue
        """
        # TODO: Make default handling to add warnings to the result for these extra_arguments
        pass

    # --- private methods ---

    def _abort_in_case_of_errors(self, result):
        if result.has_errors():
            self._return_from_command()

    def _return_from_command(self):
        raise EarlyReturnBecauseOfErrorsException()

    def _initial_required_parameter_names(self):
        """
        Answer the names of the required parameters.
        If my subclass has one or more required parameters,
        it should override me answering the names of that/those parameter/s.

        :return: set of str
        """
        return set()

    def _execute_from_successful_parameter_validation(self, result):
        """
        My subclass should override me. Performs the operation and answers the result of the execution

        :return: result of execution
        """
        return result

    def _initial_parameters(self):
        """
        If I have more than 0 parameters, I should answer the definition of that/those parameter/s.

        :rtype: list of Parameter
        """
        return []

    def _initial_at_least_one_required_sets(self):
        """Answer a list of sets. Each set with the names of parameters from which al least one is required"""
        return []

    def _default_arguments(self):
        """Answer a dictionary with the default command arguments"""
        return {}

    def _validate_parameters_and_arguments(self, result):
        return self._parameters.validate_parameters_and_arguments(result)
