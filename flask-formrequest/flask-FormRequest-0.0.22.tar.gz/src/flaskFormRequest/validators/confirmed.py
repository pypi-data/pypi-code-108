from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Confirmed(Validator):
    def __init__(self, suffix: str = '_confirmation', message: Union[str, None] = None, parse: bool = True) -> None:
        self.suffix = suffix
        self.parse = parse
        self.message = message or 'This field confirmation does not match.'

    def handler(self, value, field, request):
        field_to_match = self.data.get(f'{field}{self.suffix}')
        if value != field_to_match:
            raise ValidationError(self.message)
