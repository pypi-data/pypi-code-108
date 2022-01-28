import logging

from django.db.models import Model

from isc_common.fields.code_field import CodeField

logger = logging.getLogger(__name__)


class Param_type(Model):
    code = CodeField(unique=True, db_index=True)

    def __str__(self):
        return f"(id: {self.id}, code: {self.code})"

    class Meta:
        verbose_name = 'Типы параметров'
