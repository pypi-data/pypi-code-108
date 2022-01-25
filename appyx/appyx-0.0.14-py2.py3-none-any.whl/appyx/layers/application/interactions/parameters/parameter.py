from typing import List

from appyx.layers.application.interactions.validators.parameters import ParameterValidator
from appyx.layers.domain.result import Result


class Parameter:
    """
    Models one requirement of an interaction or operation.
    It has a name and a way to tell if it is valid (i.e. the requirement fulfilled) by an argument.

    Example:
        If I have a money deposit operation, with two parameters: amount and currency
        the parameter amount would have as requirement to be a number, maybe non-negative or positive
        the parameter currency would have as requirement to be one of the possible currencies in the system.
        The arguments 100 and "USD" would satisfy those parameters, they would be valid.
        The arguments "one-hundred" and "MoneyMoneyMoney" would not.
    """

    def __init__(self, name: str, validators: List[ParameterValidator] = None, description='', example_argument=None):
        super().__init__()
        self._name = name
        self._validators = validators if type(validators) is list else []
        self._description = description
        self._example_argument = example_argument

    def example_argument(self):
        return self._example_argument

    def validate(self, argument, result=None) -> Result:
        if result is None:
            result = Result()

        validators_result = Result()
        for validator in self._validators:
            validator.validate(argument, validators_result, self._name)

        result.add_errors(validators_result.errors())
        return result

    def name(self):
        return self._name

    def description(self):
        return self._description

    def has_example_argument(self):
        return self._example_argument is not None
