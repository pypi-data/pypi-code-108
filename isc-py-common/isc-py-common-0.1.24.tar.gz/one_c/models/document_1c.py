import logging

from django.db.models import UUIDField, Model

from isc_common.fields.related import ForeignKeyProtect
from one_c.models.entity_1c import Entity_1c

logger = logging.getLogger(__name__)


class Document_1c(Model):
    entity = ForeignKeyProtect(Entity_1c)
    ref = UUIDField(primary_key=True)

    def __str__(self):
        return f"(ref: {self.ref}, entity: {self.entity})"

    class Meta:
        verbose_name = 'Документ'
