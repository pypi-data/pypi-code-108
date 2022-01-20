from json import dumps
from django.db import models
from django.db.models import Model

from wikibase.ir.django_property import DjangoProperty
from functools import lru_cache


class DjangoModel(dict):

    @lru_cache(maxsize=1024)
    def __init__(self, model: Model):
        dict.__init__(self,
                      type=f'{model.__module__}.{model._meta.object_name}',
                      table_name=model._meta.db_table,
                      application=model._meta.app_label,
                      fields=[DjangoProperty(field, DjangoModel) for field in model._meta.concrete_fields])

    def __repr__(self) -> str:
        return dumps(self)

    def __hash__(self):
        if len(self) == 0:
            return 0
        return hash(str(self['application'] + '/' + self['table_name']))

    def __eq__(self, other):
        return len(self) == len(other) and (len(self) == 0 or (self['application'] == other['application'] and self['table_name'] == other['table_name']))
