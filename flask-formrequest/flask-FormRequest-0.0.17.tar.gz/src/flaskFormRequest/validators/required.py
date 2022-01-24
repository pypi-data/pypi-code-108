from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Required(Validator):
    def __init__(self, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field is required'

    def handler(self, value, field, request):
        if value is None or len(value) == 0:
            raise StopValidation(self.message)
