from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from appyx.layers.application.interactions.parameters.parameter import Parameter
from appyx.layers.domain.errors import BaseErrorFactory
from appyx.layers.domain.result import Result


class ParametersValidator:
    """
        I validate the command's parameters
    """

    def validate(self, parameters_and_arguments, result) -> Result:
        validation_result = self._validation_result(parameters_and_arguments)
        if validation_result.is_successful():
            self._on_valid_argument(parameters_and_arguments, validation_result, result)
        else:
            self._on_invalid_argument(parameters_and_arguments, validation_result, result)
        return result

    def _validation_result(self, parameters_and_arguments) -> Result:
        raise NotImplementedError("subclass responsibility")

    def _on_valid_argument(self, parameters_and_arguments, validation_result, result):
        pass

    def _on_invalid_argument(self, parameters_and_arguments, validation_result, result):
        result.add_error(BaseErrorFactory().parameters_validation_error(parameters_and_arguments,
                                                                        validation_result.errors()))


class NoneValidation(ParametersValidator):
    def validate(self, parameters_and_arguments, result):
        return result


class RequiredParameters(ParametersValidator):
    """
        I validate the required command's parameters
    """

    def __init__(self, required_parameters: List[Parameter]):
        super().__init__()
        self._required_parameters = required_parameters

    def _validation_result(self, parameters_and_arguments):
        validation_result = Result()
        for parameter_name in self._required_parameters:
            if parameter_name not in parameters_and_arguments.keys():
                validation_result.add_error(u'The parameter %s is required' % parameter_name)
        return validation_result

    @classmethod
    def new_with(cls, required_parameters):
        return cls(required_parameters)


class AtLeastOneParameterRequired(ParametersValidator):
    """
        I validate that the command has at least one of its required parameters.
    """

    def __init__(self, required_parameters):
        super().__init__()
        self._required_parameters = required_parameters

    def _validation_result(self, parameters_and_arguments):
        validation_result = Result()
        for parameter_name in self._required_parameters:
            if parameter_name in parameters_and_arguments.keys():
                return validation_result
        validation_result.add_error(
            u'At least one of the following parameters is required: {0}.'.format(u', '.join(self._required_parameters)))
        return validation_result


class AtLeastOneParameterNotNoneRequired(ParametersValidator):
    """
        I validate that the command has at least one of its required parameters set as not None.
    """

    def __init__(self, required_parameters):
        super().__init__()
        self._required_parameters = required_parameters

    def _validation_result(self, parameters_and_arguments):
        validation_result = Result()
        for parameter_name in self._required_parameters:
            if parameter_name in parameters_and_arguments.keys():
                argument = parameters_and_arguments[parameter_name]
                if argument is not None:
                    return validation_result
        validation_result.add_error(
            u'At least one of the following parameters is required and not none: {0}.'.format(
                u', '.join(self._required_parameters)))
        return validation_result


class ParameterValidator:
    """
    Models a validator for a parameter.
    """

    def validate(self, argument: object, result: Result = None, parameter_name: str = None) -> bool:
        if argument is None:
            return True

        result = self.validate_with_result(argument, result, parameter_name)
        return result.is_successful()

    def validate_with_result(self, argument: object, result: Result = None, parameter_name: str = None) -> Result:
        if result is None:
            result = Result()

        return self._validate_with_result(argument, result, parameter_name)

    def _validate_with_result(self, argument, result, parameter_name):
        validation_result = self._validation_result(argument)
        if validation_result.is_successful():
            self._on_valid_argument(argument, validation_result, result, parameter_name)
        else:
            self._on_invalid_argument(argument, validation_result, result, parameter_name)
        return result

    def _on_invalid_argument(self, argument, validation_result, result, parameter_name):
        if parameter_name is None:
            parameter_name = self.__class__.__name__

        result.add_error(BaseErrorFactory().parameter_validation_error(parameter_name, argument,
                                                                       validation_result.errors()))

    def _validation_result(self, argument: object) -> Result:
        raise NotImplementedError('subclass responsibility')

    def _on_valid_argument(self, argument: object, validation_result: Result, result: Result, parameter_name: str):
        pass
