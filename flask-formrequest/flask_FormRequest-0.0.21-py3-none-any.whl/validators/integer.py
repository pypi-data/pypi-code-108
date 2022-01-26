from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Integer(Validator):
    def __init__(self, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field must be an integer.'

    def parse_data(self, value):
        return int(value)

    def handler(self, value, field, request):
        try:
            assert not isinstance(value, float)
            value = int(value)
        except:
            raise StopValidation(self.message)
