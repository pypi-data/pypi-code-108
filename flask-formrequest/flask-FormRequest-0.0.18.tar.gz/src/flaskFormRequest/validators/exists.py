from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Exists(Validator):
    def __init__(self, model,
                 column: Union[str, None] = None,
                 message: Union[str, None] = None,
                 parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This attribute is invalid'
        self.model = model
        self.column = column

    def handler(self, value, field, request):
        column = self.column or field
        filters = [getattr(self.model, column) == value]
        exists = self.model.query.filter(*filters).count()
        if not exists:
            raise ValidationError(self.message)

