from datetime import datetime
from typing import Union
from .date import Date
from .validator import Validator, ValidationError, StopValidation


class DateEquals(Validator):
    def __init__(self, date, format='%Y-%m-%d %H:%M:%S', message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This attribute is not valid'
        self.format = format
        self.date = date

    def parse_data(self, value):
        return self.dt_formated

    def handler(self, value, field, request):
        date_validator = Date(self.format, self.message)
        self.dt_formated = date_validator(value, field, self.data, request)

        if self.dt_formated != self.date:
            raise ValidationError(self.message)
