import logging

from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet

logger = logging.getLogger(__name__)


class Fragment_param_typesQuerySet(BaseRefQuerySet):
    pass


class Fragment_param_typesManager(BaseRefManager):

    @classmethod
    def getRecord(cls, record ) :
        res = {
            'code': record.code,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'id': record.id,
            'name': record.name,
        }
        return res

    def get_queryset(self):
        return Fragment_param_typesQuerySet(self.model, using=self._db)


class Fragment_param_types(BaseRef):
    objects = Fragment_param_typesManager()

    def __str__(self):
        return f'ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Типы рараметров фрагмента'
