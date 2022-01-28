import logging

from django.db.models import PositiveIntegerField

from isc_common.fields.code_field import CodeField
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet

logger = logging.getLogger(__name__)


class ShiftsQuerySet(BaseRefQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class ShiftsManager(BaseRefManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'color': record.color,
        }
        return res

    def get_queryset(self):
        return ShiftsQuerySet(self.model, using=self._db)


class Shifts(BaseRef):
    color = CodeField(null=True, blank=True)
    objects = ShiftsManager()

    def __str__(self):
        return f"ID={self.id}, code={self.code}, name={self.name}, description={self.description}, color={self.color}"

    class Meta:
        verbose_name = 'Смены'
