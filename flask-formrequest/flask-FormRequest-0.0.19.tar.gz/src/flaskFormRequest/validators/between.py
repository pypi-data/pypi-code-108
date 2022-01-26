import re
from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Between(Validator):
    number_types = (int, float)

    def __init__(self, min: int, max: int, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field is invalid'
        self.min = min
        self.max = max

    def handler(self, value, field, request):
        has_error = False
        if isinstance(value, str) or isinstance(value, list):
            has_error = len(value) < self.min or len(value) > self.max
        elif type(value) in self.number_types:
            has_error = value < self.min or value > self.max

        if has_error:
            raise ValidationError(self.message)
