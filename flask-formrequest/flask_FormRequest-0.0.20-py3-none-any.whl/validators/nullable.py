from typing import Union
from .validator import Validator, NoneValueException


class Nullable(Validator):
    def handler(self, value, field, request):
        if value is None:
            raise NoneValueException(self.message)
