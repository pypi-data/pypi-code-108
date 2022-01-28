import logging

from django.db.models import Model

from isc_common.fields.related import ForeignKeyCascade
from one_c.models.document_1c import Document_1c
from one_c.models.documents_param_1c import Documents_param_1c

logger = logging.getLogger(__name__)


class Documents_param_cross_1c(Model):
    document = ForeignKeyCascade(Document_1c)
    param = ForeignKeyCascade(Documents_param_1c)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('document', 'param'),)
