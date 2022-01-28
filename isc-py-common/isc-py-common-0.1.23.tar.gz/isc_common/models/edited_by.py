import logging

from django.db.models import BigIntegerField
from isc_common.fields.code_field import CodeStrictField
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet

logger = logging.getLogger(__name__)


class Edited_byQuerySet(AuditQuerySet):
    pass


class Edited_byManager(AuditManager):

    @classmethod
    def getRecord(cls, record ) :
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Edited_byQuerySet(self.model, using=self._db)


class Edited_by(AuditModel):
    table_id = BigIntegerField()
    table_name = CodeStrictField()
    objects = Edited_byManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Таблица сделанных изменений'
