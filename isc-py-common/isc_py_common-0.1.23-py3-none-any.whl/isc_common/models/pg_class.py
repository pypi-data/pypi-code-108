import logging

from django.db.models import Model

from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField

logger = logging.getLogger(__name__)


class Pg_class(Model):
    relname = CodeField(primary_key=True, null=False)
    relkind = NameField()

    def __str__(self):
        return f"{self.relname}"

    class Meta:
        verbose_name = 'pg_class'
        managed = False;
        db_table = 'pg_class'
