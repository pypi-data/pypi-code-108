import re
from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Boolean(Validator):
    true_types = (True, "true", 1, "1",)
    false_types = (False, "false", 0, "0")

    def __init__(self, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field must be true or false.'

    def parse_data(self, value):
        if value in self.true_types:
            return True
        elif value in self.false_types:
            return False
        else:
            return value

    def handler(self, value, field, request):
        if not value in self.true_types and not value in self.false_types:
            raise ValidationError(self.message)
