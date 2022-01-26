from typing import Union
from .validator import Validator, ValidationError, StopValidation


class CurrentPassword(Validator):
    def __init__(self, model, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'The password is incorrect.'
        self.model = model

    def handler(self, value, field, request):
        if not self.model.verify_password(value):
            raise ValidationError(self.message)
