import abc
from typing import Any, Union


class ValidationError(ValueError):
    def __init__(self, message="", *args, **kwargs):
        ValueError.__init__(self, message, *args, **kwargs)


class StopValidation(Exception):
    def __init__(self, message="", *args, **kwargs):
        Exception.__init__(self, message, *args, **kwargs)


class NoneValueException(Exception):
    def __init__(self, message="", *args, **kwargs):
        Exception.__init__(self, message, *args, **kwargs)


class Validator(abc.ABC):
    def __init__(self, message: Union[str, None] = None, parse: bool = True) -> None:
        self.data = {}
        self.parse = parse
        self.message = message or 'This field is invalid'

    def parse_data(self, value: Any) -> Any:
        return value

    @abc.abstractmethod
    def handler(self, value, field, request):
        pass

    def __call__(self, value, field, data, request):
        self.data = data
        self.field = field
        self.value = value
        self.request = request
        self.handler(self.value, self.field, self.request)
        return self.parse_data(self.value) if self.parse else self.value
