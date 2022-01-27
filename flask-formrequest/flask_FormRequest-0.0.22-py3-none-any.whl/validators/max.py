from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Max(Validator):
    def __init__(self, length: int, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.size = length
        self.message = message or 'This field is not valid.'

    def handler(self, value, field, request):
        if isinstance(value, int) or isinstance(value, float):
            value = str(value)

        # TODO: implement support for files

        if len(value) > self.size:
            raise ValidationError(self.message)
