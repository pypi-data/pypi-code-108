from typing import Union
from .validator import Validator, ValidationError, StopValidation


class Unique(Validator):
    def __init__(self,
                 model,
                 column: Union[str, None] = None,
                 except_id: Union[str, int, None] = None,
                 message: Union[str, None] = None,
                 parse: bool = True) -> None:
        self.parse = parse
        self.message = message or 'This field is not valid.'
        self.model = model
        self.column = column
        self.except_id = except_id

    def handler(self, value, field, request):
        column = self.column or field

        filters = [getattr(self.model, column) == value]
        if self.except_id is not None:
            filters.append(self.model.id != self.except_id)

        exists = self.model.query.filter(*filters).count()

        if exists:
            raise ValidationError(self.message)
