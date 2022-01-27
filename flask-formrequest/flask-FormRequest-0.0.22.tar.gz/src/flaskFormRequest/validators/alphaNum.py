import re
from typing import Union
from .validator import Validator, ValidationError, StopValidation


class AlphaNum(Validator):
    def __init__(self, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field must only contain letters and numbers.'

    def handler(self, value, field, request):
        value = str(value)
        if not value.isalnum():
            raise ValidationError(self.message)
