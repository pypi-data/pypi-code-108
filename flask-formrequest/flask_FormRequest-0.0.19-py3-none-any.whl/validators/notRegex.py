import re
from typing import Union
from .validator import Validator, ValidationError, StopValidation


class NotRegex(Validator):
    def __init__(self, pattern: str, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.pattern = pattern
        self.message = message or 'This field is not valid.'

    def handler(self, value, field, request):
        if re.match(self.pattern, value):
            raise ValidationError(self.message)
