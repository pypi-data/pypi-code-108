import logging

from isc_common.fields.code_field import ColorField
from isc_common.models.base_ref import BaseRefManager, BaseRef, BaseRefQuerySet

logger = logging.getLogger(__name__)


class Standard_colorsQuerySet(BaseRefQuerySet):
    pass


class Standard_colorsManager(BaseRefManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'code': record.code,
            'color': record.color,
            'name': record.name,
            'description': record.description,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Standard_colorsQuerySet(self.model, using=self._db)


class Standard_colors(BaseRef):
    color = ColorField(null=True, blank=True)
    objects = Standard_colorsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Предварительно установленные цвета'
