import logging

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet

logger = logging.getLogger(__name__)


class AuditHistoryQuerySet(AuditQuerySet):
    pass


class AuditHistoryManager(AuditManager):

    @classmethod
    def getRecord(cls, record):
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
        return AuditHistoryQuerySet(self.model, using=self._db)


class AuditHistory(AuditModel):
    hcreator = ForeignKeyProtect(User)

    objects = AuditHistoryManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'История изменений'
        abstract = True
