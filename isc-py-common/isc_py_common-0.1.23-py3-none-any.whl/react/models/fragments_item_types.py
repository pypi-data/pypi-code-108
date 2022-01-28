import logging

from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet

logger = logging.getLogger(__name__)


class Fragments_item_typesQuerySet(BaseRefQuerySet):
    pass


class Fragments_item_typesManager(BaseRefManager):

    @classmethod
    def getRecord(cls, record ) :
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Fragments_item_typesQuerySet(self.model, using=self._db)


class Fragments_item_types(BaseRef):
    objects = Fragments_item_typesManager()

    def __str__(self):
        return f'ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Типы элементов фрагментов'
