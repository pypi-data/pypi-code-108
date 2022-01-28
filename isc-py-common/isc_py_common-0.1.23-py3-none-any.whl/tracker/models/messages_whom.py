import logging

from django.db.models import Model

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditQuerySet, AuditManager
from tracker.models.messages import Messages

logger = logging.getLogger(__name__)


class Messages_whomQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Messages_whomManager(AuditManager):

    @classmethod
    def getRecord(cls, record ) :
        res = {}
        return res

    def get_queryset(self):
        return Messages_whomQuerySet(self.model, using=self._db)


class Messages_whom(Model):
    message = ForeignKeyCascade(Messages)
    to_whom = ForeignKeyCascade(User)

    objects = Messages_whomManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Получатель сообщения'
        unique_together = (('message', 'to_whom'),)
