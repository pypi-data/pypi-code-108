try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField

from django.db.models import CharField

from isc_common.fields import Field


class CodeField(CharField, Field):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('default', None)
        kwargs.setdefault('null', True)
        kwargs.setdefault('blank', True)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        del kwargs["db_index"]
        del kwargs['default']
        return name, path, args, kwargs


class CodeStrictField(CharField, Field):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('default', None)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        del kwargs["db_index"]
        del kwargs['default']
        return name, path, args, kwargs


class ColorField(CharField, Field):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 10)
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('default', None)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        del kwargs["db_index"]
        del kwargs['default']
        return name, path, args, kwargs


class JSONFieldIVC(JSONField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', dict)
        super().__init__(*args, **kwargs)
