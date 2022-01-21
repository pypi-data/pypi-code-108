from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Declined(Validator):
    accepted = (False, 0, "off", "no")

    def __init__(self, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field must be declined.'

    def parse_data(self, value):
        return not(value in self.accepted)

    def handler(self, value, field, request):
        if value not in self.accepted:
            raise ValidationError(self.message)
