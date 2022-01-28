import logging

from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel
from isc_common.number import DelProps

logger = logging.getLogger(__name__)


class Deleted_progressesQuerySet(AuditQuerySet):
    pass


class Deleted_progressesManager(AuditManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
            'props': record.props
        }
        return DelProps(res)

    def get_queryset(self):
        return Deleted_progressesQuerySet(self.model, using=self._db)


class Deleted_progresses(AuditModel):
    id_progress = CodeStrictField()
    user = ForeignKeyCascade(User)

    objects = Deleted_progressesManager()

    def __str__(self):
        return f'ID:{self.id}, id_progress: {self.id_progress}, user: [{self.user}]'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Отражение удаленных запущенных процессов'
        unique_together = (('user', 'id_progress'),)
