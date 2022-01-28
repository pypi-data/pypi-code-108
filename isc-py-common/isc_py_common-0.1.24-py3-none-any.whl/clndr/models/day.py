import logging

from isc_common.models.base_ref import BaseRefQuerySet, BaseRefManager, BaseRef

logger = logging.getLogger(__name__)


class DayQuerySet(BaseRefQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class DayManager(BaseRefManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
        }
        return res

    def get_queryset(self):
        return DayQuerySet(self.model, using=self._db)


class Day(BaseRef):
    objects = DayManager()

    def __str__(self):
        return f"ID={self.id}, code={self.code}, name={self.name}, description={self.description}"

    class Meta:
        verbose_name = 'День'
