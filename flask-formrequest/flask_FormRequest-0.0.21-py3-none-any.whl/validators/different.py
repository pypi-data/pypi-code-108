from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Different(Validator):
    def __init__(self, field: str, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field is not valid.'
        self.compare_field = field

    def handler(self, value, field, request):
        another_field_value = self.data.get(self.compare_field)

        if value == another_field_value:
            raise ValidationError(self.message)
