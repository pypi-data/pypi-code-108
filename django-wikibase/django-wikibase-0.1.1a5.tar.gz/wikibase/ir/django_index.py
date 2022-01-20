from json import dumps
from django.db import models
from django.db.models import Model, Index

from wikibase.ir.django_property import DjangoProperty
from wikibase.ir.django_model import DjangoModel
from functools import lru_cache


class DjangoIndex(dict):

    @lru_cache(maxsize=1024*5)
    def __init__(self, model: Model, index: dict):
        dict.__init__(self,
                      name=f'{index["name"]}',
                      model=DjangoModel(model),
                      field_names=index['fields'])

    def __repr__(self) -> str:
        return dumps(self)

    def __hash__(self):
        if len(self) == 0:
            return 0
        return hash(str(self['model']['table_name'] + '/' + self['name']))

    def __eq__(self, other):
        return len(self) == len(other) and (len(self) == 0 or (self['model']['table_name'] == other['model']['table_name'] and self['name'] == other['name']))
