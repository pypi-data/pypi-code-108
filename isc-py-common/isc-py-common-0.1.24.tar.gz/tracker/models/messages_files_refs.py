import logging

from isc_common.fields.related import ForeignKeyCascade, ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from tracker.models.messages import Messages
from tracker.models.messages_files import Messages_files

logger = logging.getLogger(__name__)


class Messages_files_refsQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Messages_files_refsManager(AuditManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
        }
        return res

    def get_queryset(self):
        return Messages_files_refsQuerySet(self.model, using=self._db)


class Messages_files_refs(AuditModel):
    message = ForeignKeyProtect(Messages)
    messages_file = ForeignKeyProtect(Messages_files)

    objects = Messages_files_refsManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('message', 'messages_file'),)
