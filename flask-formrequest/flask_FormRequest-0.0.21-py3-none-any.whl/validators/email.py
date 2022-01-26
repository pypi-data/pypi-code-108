from email_validator import validate_email, EmailNotValidError
from typing import Any, Union
from .validator import Validator, ValidationError, StopValidation


class Email(Validator):
    def __init__(self, message: Union[str, None] = None, parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field must be a valid email address.'

    def handler(self, value, field, request):
        try:
            valid = validate_email(value)
            self.value = valid.email
        except EmailNotValidError as e:
            raise ValidationError(self.message)
