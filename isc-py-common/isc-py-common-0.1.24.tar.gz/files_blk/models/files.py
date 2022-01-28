import logging

from django.db.models import Model, TextField, Manager, PositiveIntegerField
from isc_common.fields.related import ForeignKeyCascade
from files_blk.models.files_group import Files_group
from isc_common.models.audit import AuditModel

logger = logging.getLogger(__name__)


class Files(AuditModel):
    path = TextField(db_index=True)
    file_size = PositiveIntegerField()
    group = ForeignKeyCascade(Files_group)

    objects = Manager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Файлы'
