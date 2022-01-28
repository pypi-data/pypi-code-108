import logging

from django.db.models import BooleanField, TimeField

from isc_common.fields.code_field import CodeField
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet

logger = logging.getLogger(__name__)


class Day_typesQuerySet(BaseRefQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Day_typesManager(BaseRefManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'color': record.color,
            'isholiday': record.isholiday,
            'length': record.length,
        }
        return res

    def get_queryset(self):
        return Day_typesQuerySet(self.model, using=self._db)


class Day_types(BaseRef):
    isholiday = BooleanField(default=False)
    length = TimeField(null=True, blank=True)
    color = CodeField()
    objects = Day_typesManager()

    def __str__(self):
        return f"ID={self.id}, code={self.code}, name={self.name}, description={self.description}, color={self.color}, isholiday={self.isholiday}, length={self.length}"

    class Meta:
        verbose_name = 'Типы дней'
