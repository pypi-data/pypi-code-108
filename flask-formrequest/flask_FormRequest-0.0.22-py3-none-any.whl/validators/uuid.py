from typing import Union
from uuid import UUID as UUIDHelper
from .validator import Validator, ValidationError, StopValidation


class UUID(Validator):
    def __init__(self, version: int = 4, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field must be a valid UUID'
        self.version = version

    def parse_data(self, value):
        return UUIDHelper(value, version=self.version)

    def handler(self, value, field, request):
        try:
            value = UUIDHelper(value, version=self.version)
        except ValueError:
            raise StopValidation(self.message)
