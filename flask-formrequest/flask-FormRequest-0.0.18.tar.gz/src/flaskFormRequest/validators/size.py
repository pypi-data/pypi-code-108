from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Size(Validator):
    def __init__(self, length: int, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.size = length
        self.message = message or 'The :attribute must be :size characters.'

    def handler(self, value, field, request):
        if len(value) != self.size:
            raise ValidationError(self.message)
