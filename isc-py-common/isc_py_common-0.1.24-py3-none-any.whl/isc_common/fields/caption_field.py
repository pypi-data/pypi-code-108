from django.db.models import CharField
from django.utils.translation import gettext_lazy as _


class CaptionField(CharField):
    description = "Наименованиме"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        kwargs.setdefault('db_index', True)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        del kwargs["db_index"]
        return name, path, args, kwargs
