import logging

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet

logger = logging.getLogger(__name__)


class Message_user_2_userQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Message_user_2_userManager(AuditManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'user_reciver_id': record.user_reciver.id,
            'user_reciver__username': record.user_reciver.username,
            'user_reciver__first_name': record.user_reciver.first_name,
            'user_reciver__last_name': record.user_reciver.last_name,
            'user_reciver__middle_name': record.user_reciver.middle_name,
        }
        return res

    def get_queryset(self):
        return Message_user_2_userQuerySet(self.model, using = self._db)


class Message_user_2_user(AuditModel):
    user_sender = ForeignKeyCascade(User, related_name = 'user_sender')
    user_reciver = ForeignKeyCascade(User, related_name = 'user_reciver')

    objects = Message_user_2_userManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Доступ к получателям сообщений'
