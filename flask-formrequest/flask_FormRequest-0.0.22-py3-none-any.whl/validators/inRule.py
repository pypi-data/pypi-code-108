from typing import Union
from .validator import Validator, ValidationError, StopValidation


class In(Validator):
    def __init__(self, accepted_values = Union[list, tuple], message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field is not valid.'
        self.accepted_values = accepted_values

    def handler(self, value, field, request):
        if value not in self.accepted_values:
            raise ValidationError(self.message)
