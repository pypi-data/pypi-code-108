import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.base_ref import BaseRefManager, BaseRefQuerySet, BaseRefHierarcy
from react.models.fragments_item_types import Fragments_item_types

logger = logging.getLogger(__name__)


class Fragments_viewQuerySet(BaseRefQuerySet):
    pass


class Fragments_viewManager(BaseRefManager):
    @classmethod
    def getRecord(cls, record ) :
        res = {
            'code': record.code,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'id': record.id,
            'name': record.name,
            'parent_id': record.parent.id if record.parent else None,
            'type__name': record.type.name,
            'type_id': record.type.id,
        }
        return res

    def get_queryset(self):
        return Fragments_viewQuerySet(self.model, using=self._db)


class Fragments_view(BaseRefHierarcy):
    # page = ForeignKeyProtect(Pages)
    type = ForeignKeyProtect(Fragments_item_types)

    objects = Fragments_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Структура фрагмента'
        db_table = 'react_fragments_view'
        managed = False
