from appyx.layers.application.interactions.validators.parameters import AtLeastOneParameterRequired, \
    AtLeastOneParameterNotNoneRequired
from appyx.layers.domain.errors import BaseErrorFactory
from appyx.layers.domain.messages.exceptions import ArgumentNotFound, ParameterNotFoundException, \
    DuplicateParameterException


class SetOfParameters:
    """
    I model the set of parameters and arguments that a context handles.
    I handle the definition and validation of the arguments based on the validations each parameter has defined.

    _context: object responsible to handle unexpected arguments
    _parameters: list of parameters that compose me
    _arguments = dictionary of names and values for the parameters I have
    _required_parameter_names: list of names of parameters that should be present in arguments
    _parameters_validators = list of validators that apply to all parameters and arguments as a whole

    Note:
        Parameter is the "slot" that I have for a value. It has a name and validators.
        Argument is the value for that parameter.
    """

    def __init__(self, context, initial_parameters=None,
                 initial_required_parameter_names=None, initial_at_least_one_required_sets=None,
                 default_arguments=None):
        _initial_parameters = initial_parameters or []
        _initial_required_parameter_names = initial_required_parameter_names or set()
        _initial_at_least_one_required_sets = initial_at_least_one_required_sets or []
        self._context = context
        self._parameters = _initial_parameters
        self._arguments = default_arguments or {}
        self._required_parameter_names = _initial_required_parameter_names
        self._parameters_validators = []
        for set_of_names in _initial_at_least_one_required_sets:
            self.add_at_least_one_constraint(set_of_names)

    def set_arguments(self, arguments):
        """Set the values that each parameter will have.
        Arguments is a dictionary with the names of the parameters as keys and the value of the argument as value.

        :param arguments: dict of str: object
        """
        self._arguments = arguments

    def update_arguments(self, arguments):
        """Updates the values that each parameter will have.
        Arguments is a dictionary with the names of the parameters as keys and the value of the argument as value.

        :param arguments: dict of str: object
        """
        self._arguments.update(arguments)

    def set_argument_value(self, argument_name, value):
        """Set the value for a specific argument.

        :param argument_name: str
        :param value: object
        """
        self._arguments[argument_name] = value

    def add_parameter(self, parameter):
        if parameter.name() is None:
            raise ValueError('Parameter cannot be None')
        if parameter.name() == '':
            raise ValueError('Parameter cannot be an empty string')
        is_parameter_already_present = self.get_parameter_named(parameter.name()) is not None
        if is_parameter_already_present:
            raise DuplicateParameterException(parameter.name())
        self._parameters.append(parameter)

    def get_parameter_named(self, name):
        """Answers the parameter with name <name>.
        Answers None if no parameter with that named is found.

        :param name: str
        :return: Parameter or none
        """
        parameter = None
        for param in self._parameters:
            if param.name() == name:
                parameter = param
        return parameter

    def add_required_parameter_named(self, parameter_name):
        """Define parameter named <parameter_name> as required.

        :param parameter_name: str
        """
        self._required_parameter_names.add(parameter_name)

    def add_required_parameters_named(self, parameter_name_list):
        """Define parameters named [<parameter_name>] as required.

        :param parameter_name_list: List<str>
        """
        for parameter_name in parameter_name_list:
            self.add_required_parameter_named(parameter_name)

    def remove_required_parameter_named(self, parameter_name):
        """Remove the required restriction for parameter named <parameter_name>.

        :param parameter_name: str
        """
        self._required_parameter_names.remove(parameter_name)

    def required_parameter_names(self):
        return self._required_parameter_names

    def add_at_least_one_constraint(self, parameter_names):
        """Add a restriction that at least on of parameter_names should be required.

        :param parameter_names: list of str
        """
        self.assert_all_parameter_names_are_present(parameter_names)
        self.add_parameters_validator(AtLeastOneParameterRequired(parameter_names))

    def add_at_least_one_not_none_constraint(self, parameter_names):
        """Add a restriction that at least on of parameter_names should be required and not none.

        :param parameter_names: list of str
        """
        self.assert_all_parameter_names_are_present(parameter_names)
        self.add_parameters_validator(AtLeastOneParameterNotNoneRequired(parameter_names))

    def add_parameters_validator(self, validator):
        """Add a validator that analysis the parameters and arguments as a whole"""
        self._parameters_validators.append(validator)

    def validate_parameters_and_arguments(self, result):
        """
        Run validations of all arguments against all parameters and answer the result of such analysis.

        :param result: Result
        :return: Result
        """
        self._validate_unexpected_arguments(result)
        self._validate_missing_arguments(result)
        self._validate_present_arguments(result)

        if result.is_successful():
            self._apply_validators_for_parameters_set(result)

        return result

    def is_defined_argument_named(self, argument_name):
        return argument_name in self._arguments

    def get_argument_named(self, argument_name):
        if self.is_defined_argument_named(argument_name):
            return self._arguments[argument_name]
        else:
            raise ArgumentNotFound(argument_name)

    def size(self):
        """Answer the amount of parameters the receiver has.

        :return: int
        """
        return len(self._parameters)

    def clear_parameters(self):
        self._parameters = []

    def items(self):
        return self._arguments.items()

    def parameters_missing_examples(self):
        return [parameter for parameter in self._parameters if not parameter.has_example_argument()]

    def argument_examples(self):
        argument_examples = {}
        for parameter in self._parameters:
            argument_examples[parameter.name()] = parameter.example_argument()
        return argument_examples

    def assert_all_parameter_names_are_present(self, parameter_names):
        """Note: We delegate the raise of the exception to _parameter_named"""
        for name in parameter_names:
            self._parameter_named(name)

    def validate_arguments_existence(self, arguments, result):
        parameters_names = self._parameters_names()
        arguments_names = arguments.keys()
        missing_arguments = list(set(parameters_names) - set(arguments_names))
        self._handle_missing_arguments(missing_arguments, result)

    def validate_argument_values(self, arguments, result):
        for parameter in self._parameters:
            parameter_name = parameter.name()
            parameter_is_present = parameter_name in arguments.keys()
            if parameter_is_present:
                value = arguments[parameter_name]
                parameter.validate(value, result)

    def validate(self):
        from appyx import Result
        result = Result()
        self.validate_arguments_existence(self._arguments, result)
        if result.has_errors():
            return result
        self.validate_argument_values(self._arguments, result)
        return result

    # --- private methods ---

    def _validate_unexpected_arguments(self, result):
        parameters_names = self._parameters_names()
        arguments_names = self._arguments.keys()
        unexpected_arguments = list(set(arguments_names) - set(parameters_names))
        there_are_unexpected_parameters = len(unexpected_arguments) > 0
        if there_are_unexpected_parameters:
            # Do something with the extra parameters
            self._handle_unexpected_arguments(unexpected_arguments, result)

    def _handle_unexpected_arguments(self, extra_arguments, result):
        self._context.handle_unexpected_arguments(extra_arguments, result)

    def _validate_missing_arguments(self, result):
        self.validate_arguments_existence(self._arguments, result)

    def _handle_missing_arguments(self, missing_arguments, result):
        for argument in missing_arguments:
            parameter = self._parameter_named(argument)
            if parameter.name() in self.required_parameter_names():
                result.add_error(
                    BaseErrorFactory().parameter_missing_error(u"El parámetro {0} es obligatorio".format(argument)))

    def _parameter_named(self, argument):
        for parameter in self._parameters:
            if parameter.name() == argument:
                return parameter
        raise ParameterNotFoundException(missing_parameter_name=argument)

    def _parameters_names(self):
        names = [parameter.name() for parameter in self._parameters]
        return names

    def _validate_present_arguments(self, result):
        self.validate_argument_values(self._arguments, result)

    def _apply_validators_for_parameters_set(self, result):
        for validator in self._parameters_validators:
            validator.validate(self._arguments, result)
