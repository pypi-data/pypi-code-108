import logging

from django.db.models import TextField, FloatField, DateTimeField, IntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from refs.models.type_param import Type_param

logger = logging.getLogger(__name__)


class Type_param_valuesQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Type_param_valuesManager(AuditManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'type_id': record.type.id,
            'type__code': record.type.code,
            'type__name': record.type.name,
            'type__type': record.type.type,
            'type__pick_list': record.pick_list,
            'type__length': record.length,
            'type__precision': record.precision,
            'type__exponent': record.exponent,
            'value_str': record.value_str,
            'value_float': record.value_float,
            'value_int': record.value_int,
            'value_date': record.value_date,
        }
        return res

    def get_queryset(self):
        return Type_param_valuesQuerySet(self.model, using=self._db)


class Type_param_values(AuditModel):
    type = ForeignKeyProtect(Type_param)
    value_str = TextField(null=True, blank=True)
    value_float = FloatField(null=True, blank=True)
    value_int = IntegerField(null=True, blank=True)
    value_date = DateTimeField(null=True, blank=True)

    objects = Type_param_valuesManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Значение параметров'
