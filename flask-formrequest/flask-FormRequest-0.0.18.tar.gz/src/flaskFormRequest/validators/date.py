from datetime import datetime
from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Date(Validator):
    def __init__(self, format='%Y-%m-%d', message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This attribute is not a valid date.'
        self.format = format

    def parse_data(self, value):
        return self.dt_formated

    def handler(self, value, field, request):
        try:
            self.dt_formated = datetime.strptime(value, self.format)
        except:
            raise ValidationError(self.message)
