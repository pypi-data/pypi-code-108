from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Float(Validator):
    def __init__(self, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field must be an float number.'

    def parse_data(self, value):
        return float(value)

    def handler(self, value, field, request):
        try:
            value = float(value)
        except:
            raise StopValidation(self.message)
