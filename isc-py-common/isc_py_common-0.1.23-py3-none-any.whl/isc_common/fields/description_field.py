from django.db.models import TextField

from isc_common import delAttr
from isc_common.fields import Field


class DescriptionField(TextField, Field):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('null', True)
        kwargs.setdefault('blank', True)
        kwargs.setdefault('db_index', False)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        delAttr(kwargs, 'null')
        delAttr(kwargs, 'blank')
        return name, path, args, kwargs
