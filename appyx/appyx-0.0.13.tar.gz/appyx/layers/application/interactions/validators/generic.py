import datetime
from decimal import Decimal
from typing import Iterable

from appyx.layers.application.interactions.validators.parameters import ParameterValidator
from appyx.layers.domain.result import Result


class NotNone(ParameterValidator):

    def validate(self, argument, result=None, parameter_name=None):
        """Nota: Sobrecargamos el método padre porque no queremos que nos puenteen la validacion si el argumento es None
        """
        if result is None:
            result = Result()
        return self.validate_with_result(argument, result, parameter_name)

    def _validation_result(self, argument):
        validation_result = Result()
        condition = argument is not None
        if not condition:
            validation_result.add_error(self.error_message())
        return validation_result

    @classmethod
    def error_message(cls):
        return 'Este campo no puede estar vacío'


class NotEmptyString(ParameterValidator):
    def _validation_result(self, argument):
        validation_result = Result()
        condition = argument != ""
        if not condition:
            validation_result.add_error(self.error_message())
        return validation_result

    @classmethod
    def error_message(cls):
        return 'Este campo no puede estar en blanco'


class IsString(ParameterValidator):
    def _validation_result(self, argument):
        validation_result = Result()
        condition = isinstance(argument, str)
        if not condition:
            validation_result.add_error(self.error_message())
        return validation_result

    @classmethod
    def error_message(cls):
        return 'Este campo debe ser un string'


class IsAPositiveInteger(ParameterValidator):
    def _validation_result(self, argument):
        validation_result = Result()
        condition = isinstance(argument, int) and argument >= 0

        if not condition:
            validation_result.add_error(self.error_message())

        return validation_result

    @classmethod
    def error_message(cls):
        return 'Este campo debe ser un entero positivo'


class IsBoolean(ParameterValidator):
    def _validation_result(self, argument):
        validation_result = Result()
        condition = isinstance(argument, bool)
        if not condition:
            validation_result.add_error(self.error_message())
        return validation_result

    @classmethod
    def error_message(cls):
        return 'Este campo debe ser un booleano'


class IsList(ParameterValidator):
    def __init__(self, item_validators=None) -> None:
        super().__init__()
        self._item_validators = item_validators or []

    def _validation_result(self, argument: Iterable):
        validation_result = Result()
        condition = isinstance(argument, list)
        if not condition:
            validation_result.add_error(self.error_message())
            return validation_result

        for list_item in argument:
            for validator in self._item_validators:
                validator.validate(list_item, validation_result)

        return validation_result

    @classmethod
    def error_message(cls):
        return 'Este campo debe ser una lista'


class IsDictionary(ParameterValidator):
    """
    Note: we could add support to validate keys and/or values
    """

    def __init__(self) -> None:
        super().__init__()

    def _validation_result(self, argument: Iterable):
        validation_result = Result()
        condition = isinstance(argument, dict)
        if not condition:
            validation_result.add_error(self.error_message())
            return validation_result

        return validation_result

    @classmethod
    def error_message(cls):
        return 'Este campo debe ser un diccionario'


class IsAnID(ParameterValidator):
    def _validation_result(self, argument):
        validation_result = Result()
        is_int_gte_to_1 = isinstance(argument, int) and argument >= 1
        is_str_gte_to_1 = isinstance(argument, str) and argument.isdigit() and int(argument) >= 1
        if not (is_int_gte_to_1 or is_str_gte_to_1):
            validation_result.add_error(self.error_message())
        return validation_result

    @classmethod
    def error_message(cls):
        return 'Este campo debe ser un ID válido'


class IsAFiniteDecimal(ParameterValidator):
    def _validation_result(self, argument):
        validation_result = Result()
        condition = isinstance(argument, Decimal) and argument.is_finite()
        if not condition:
            validation_result.add_error(self.error_message())
        return validation_result

    @classmethod
    def error_message(cls):
        return 'Este campo debe ser un número válido'


class NotEmpty(ParameterValidator):
    def _validation_result(self, argument):
        validation_result = Result()
        if len(argument) == 0:
            validation_result.add_error(self.error_message())
        return validation_result

    @classmethod
    def error_message(cls):
        return 'Este campo no puede ser vacio'


class AllIncluded(ParameterValidator):

    def __init__(self, items) -> None:
        super().__init__()
        self._items = items

    @classmethod
    def new_with(cls, items):
        return cls(items)

    def _validation_result(self, argument):
        validation_result = Result()
        not_included = [each for each in argument if each not in self._items]
        if not_included:
            not_included_as_string = ", ".join(not_included)
            validation_result.add_error(f"{not_included_as_string} are not valid items")
        return validation_result


class IsADateString(ParameterValidator):
    def __init__(self, pattern='%Y-%m-%dT%H:%M:%S.%fZ'):
        self._pattern = pattern

    def _validation_result(self, argument):
        validation_result = Result()
        try:
            datetime.datetime.strptime(argument, self._pattern)
        except (TypeError, ValueError):
            validation_result.add_error(self.error_message(self._pattern))
        return validation_result

    @classmethod
    def error_message(cls, pattern):
        return f'Este campo debe ser una fecha válida con formato "{pattern}"'


class IsTelephoneNumber(ParameterValidator):
    def _validation_result(self, argument):
        validation_result = Result()
        if type(argument) is not str:
            validation_result.add_error("Field is not a string")
            return validation_result

        condition = len(argument) >= 8
        if not condition:
            validation_result.add_error(self.error_message())
        return validation_result

    @classmethod
    def error_message(cls):
        return 'El teléfono es inválido'


class IsEmailAddress(ParameterValidator):
    """Modela la validacion de si una string es una direccion valida de email.

    Nota: acoplados con Django
    Nota2: Existe un package "validate_email" que hace precisamente esto.
    """

    def _validation_result(self, argument):
        validation_result = Result()

        from django.core.validators import EmailValidator
        from django.core.exceptions import ValidationError
        try:
            EmailValidator().__call__(argument)
        except ValidationError as exception:
            validation_result.add_error(str(exception.messages))
        return validation_result


class IsValidContentType(ParameterValidator):
    def __init__(self, content_types):
        self._valid_content_types = content_types

    def _validation_result(self, argument):
        validation_result = Result()
        content_type = argument.content_type
        if content_type not in self._valid_content_types:
            valid_content_types = ", ".join(str(content_type) for content_type in self._valid_content_types)
            validation_result.add_error(
                f'The content type "{content_type}" is not supported. It should be one of "{valid_content_types}"')

        return validation_result

    @classmethod
    def with_content_types(cls, content_types):
        return cls(content_types)


class MinimumValue(ParameterValidator):
    def __init__(self, value):
        self._value = value

    def _validation_result(self, argument):
        validation_result = Result()
        if argument < self._value:
            validation_result.add_error(f'Value must be greater or equal than {self._value}. Value was {argument}.')

        return validation_result


class MaximumValue(ParameterValidator):
    def __init__(self, value):
        self._value = value

    def _validation_result(self, argument):
        validation_result = Result()
        if argument > self._value:
            validation_result.add_error(f'Value must be less or equal than {self._value}. Value was {argument}.')

        return validation_result


class MinimumLength(ParameterValidator):
    def __init__(self, min_length):
        self._min_length = min_length

    def _validation_result(self, argument):
        validation_result = Result()
        argument_length = len(argument)
        if argument_length < self._min_length:
            validation_result.add_error(
                f'Value must be of longer or equal length than {self._min_length} characters.'
                f'Value was {argument_length} characters long.')

        return validation_result


class IsOneOfThese(ParameterValidator):
    def __init__(self, list_of_valid_elements):
        self._list_of_valid_elements = list_of_valid_elements

    def _validation_result(self, element):
        validation_result = Result()
        is_one_of_these = element in self._list_of_valid_elements
        if not is_one_of_these:
            valid_elements = ", ".join(str(element) for element in self._list_of_valid_elements)
            validation_result.add_error(f'Value "{element}" must be one of these elements: "{valid_elements}"')

        return validation_result


class MaximumLength(ParameterValidator):
    def __init__(self, max_length):
        self._max_length = max_length

    def _validation_result(self, argument):
        validation_result = Result()
        argument_length = len(argument)
        if self._max_length < argument_length:
            validation_result.add_error(
                f'Value must be shorter or equal length than {self._max_length} characters.'
                f'Value was {argument_length} characters long.')

        return validation_result
