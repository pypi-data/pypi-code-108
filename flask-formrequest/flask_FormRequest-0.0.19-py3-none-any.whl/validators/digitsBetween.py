from typing import Any, Union
from .validator import Validator, ValidationError, StopValidation


class DigitsBetween(Validator):
    def __init__(self, min: int, max: int, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field is not valid.'
        self.min = min
        self.max = max

    def parse_data(self, value: Any) -> int:
        return int(value)

    def handler(self, value, field, request):
        len_value = len(value)
        if not value.isnumeric() or len_value < self.min or len_value > self.max:
            raise ValidationError(self.message)
