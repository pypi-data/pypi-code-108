import logging

from django.db.models import Manager, TextField
from isc_common.models.audit import AuditModel

logger = logging.getLogger(__name__)


class Files_group(AuditModel):
    code = TextField(db_index=True)

    objects = Manager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Группы файлов'
