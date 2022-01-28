import logging

from isc_common.fields.related import ForeignKeyCascade, ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from tracker.models.messages_theme import Messages_theme
from twits.models.chat_user_user import Chat_user_user

logger = logging.getLogger(__name__)


class Chat_user_user_themeQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Chat_user_user_themeManager(AuditManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
        }
        return res

    def get_queryset(self):
        return Chat_user_user_themeQuerySet(self.model, using=self._db)


class Chat_user_user_theme(AuditModel):
    chat_user_user = ForeignKeyCascade(Chat_user_user)
    theme = ForeignKeyProtect(Messages_theme)

    objects = Chat_user_user_themeManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Кросс таблтца'
        unique_together = (('chat_user_user', 'theme'),)
