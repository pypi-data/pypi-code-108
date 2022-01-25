from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Accepted(Validator):
    accepted = (True, 1, "yes", "on")

    def __init__(self, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field must be accepted.'

    def parse_data(self, value):
        return value in self.accepted

    def handler(self, value, field, request):
        if value not in self.accepted:
            raise ValidationError(self.message)
