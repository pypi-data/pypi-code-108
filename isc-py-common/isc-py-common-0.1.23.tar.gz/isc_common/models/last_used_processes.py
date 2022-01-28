import logging

from django.db.models import BigIntegerField

from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditQuerySet, AuditManager

logger = logging.getLogger(__name__)


class Last_used_processesQuerySet(AuditQuerySet):
    pass


class Last_used_processesManager(AuditManager):
    def get_queryset(self):
        return Last_used_processesQuerySet(self.model, using=self._db)

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
        }
        return res


class Last_used_processes(AuditModel):
    user = ForeignKeyCascade(User)
    key = CodeField()
    process = BigIntegerField(db_index=True)

    objects = Last_used_processesManager()

    def __str__(self):
        return f"{self.key}: {self.value}"

    class Meta:
        verbose_name = 'Сохраненные параметры'
        unique_together = (('user', 'key', 'process'),)
