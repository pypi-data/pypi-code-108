import logging

from django.db.models import Model, PositiveIntegerField

from isc_common.fields.code_field import CodeField

logger = logging.getLogger(__name__)


class Mat_view(Model):
    schemaname = CodeField()
    relname = CodeField(primary_key=True,null=False, blank=False)
    ownername = CodeField()
    refresh_order = PositiveIntegerField()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Mat Views'
        managed = False
        db_table = 'mat_view_refresh_order'
