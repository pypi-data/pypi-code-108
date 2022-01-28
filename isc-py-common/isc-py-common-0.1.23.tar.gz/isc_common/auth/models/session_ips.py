import logging

from django.contrib.sessions.models import Session
from django.db.models import CharField

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditManager, AuditModel, AuditQuerySet

logger = logging.getLogger(__name__)


class SessionIPSQuerySet(AuditQuerySet):
    pass


class SessionIPSManager(AuditManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
        }
        return res

    def get_queryset(self):
        return SessionIPSQuerySet(self.model, using=self._db)


class SessionIPS(AuditModel):
    ip = CharField(max_length=20)
    session = ForeignKeyCascade(Session)
    user = ForeignKeyCascade(User)

    objects = SessionIPSManager()

    def __str__(self):
        return f"ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}"

    class Meta:
        verbose_name = 'Ссессти и пользователи'
