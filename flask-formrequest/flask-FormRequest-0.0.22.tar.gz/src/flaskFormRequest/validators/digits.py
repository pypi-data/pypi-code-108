from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Digits(Validator):
    def __init__(self, length: int, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field is not valid.'
        self.length = length

    def parse_data(self, value):
        return int(value)

    def handler(self, value, field, request):
        if not value.isnumeric() or len(value) != self.length:
            raise ValidationError(self.message)
