from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Alpha(Validator):
    def __init__(self, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field must only contain letters.'

    def handler(self, value, field, request):
        value = str(value)
        if not value.isalpha():
            raise ValidationError(self.message)
