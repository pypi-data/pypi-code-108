import logging

from django.db.models import TextField, Model, UUIDField, BooleanField, FloatField, IntegerField, UniqueConstraint, Q

from isc_common.fields.related import ForeignKeyProtect
from one_c.models.param_type import Param_type

logger = logging.getLogger(__name__)


class Documents_param_1c(Model):
    type = ForeignKeyProtect(Param_type)
    value = TextField(db_index=True, null=True, blank=True)
    value_boolean = BooleanField(db_index=True, null=True, blank=True)
    value_float = FloatField(db_index=True, null=True, blank=True)
    value_int = IntegerField(db_index=True, null=True, blank=True)
    value_uuid = UUIDField(db_index=True, null=True, blank=True)

    def __str__(self):
        return f"(id: {self.id}, " \
               f"document: type: {self.type}, " \
               f"value: {self.value}, " \
               f"value_uuid: {self.value_uuid}, " \
               f"value_boolean: {self.value_boolean}, " \
               f"value_float: {self.value_float}, " \
               f"value_int: {self.value_int})"

    class Meta:
        verbose_name = 'Параметры документов 1С'
        constraints = [
            UniqueConstraint(fields=['type'], condition=Q(value=None) & Q(value_boolean=None) & Q(value_float=None) & Q(value_int=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_0'),
            UniqueConstraint(fields=['type', 'value'], condition=Q(value_boolean=None) & Q(value_float=None) & Q(value_int=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_1'),
            UniqueConstraint(fields=['type', 'value_boolean'], condition=Q(value=None) & Q(value_float=None) & Q(value_int=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_2'),
            UniqueConstraint(fields=['type', 'value', 'value_boolean'], condition=Q(value_float=None) & Q(value_int=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_3'),
            UniqueConstraint(fields=['type', 'value_float'], condition=Q(value=None) & Q(value_boolean=None) & Q(value_int=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_4'),
            UniqueConstraint(fields=['type', 'value', 'value_float'], condition=Q(value_boolean=None) & Q(value_int=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_5'),
            UniqueConstraint(fields=['type', 'value_boolean', 'value_float'], condition=Q(value=None) & Q(value_int=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_6'),
            UniqueConstraint(fields=['type', 'value', 'value_boolean', 'value_float'], condition=Q(value_int=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_7'),
            UniqueConstraint(fields=['type', 'value_int'], condition=Q(value=None) & Q(value_boolean=None) & Q(value_float=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_8'),
            UniqueConstraint(fields=['type', 'value', 'value_int'], condition=Q(value_boolean=None) & Q(value_float=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_9'),
            UniqueConstraint(fields=['type', 'value_boolean', 'value_int'], condition=Q(value=None) & Q(value_float=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_10'),
            UniqueConstraint(fields=['type', 'value', 'value_boolean', 'value_int'], condition=Q(value_float=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_11'),
            UniqueConstraint(fields=['type', 'value_float', 'value_int'], condition=Q(value=None) & Q(value_boolean=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_12'),
            UniqueConstraint(fields=['type', 'value', 'value_float', 'value_int'], condition=Q(value_boolean=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_13'),
            UniqueConstraint(fields=['type', 'value_boolean', 'value_float', 'value_int'], condition=Q(value=None) & Q(value_uuid=None), name='Documents_param_1c_unique_constraint_14'),
            UniqueConstraint(fields=['type', 'value', 'value_boolean', 'value_float', 'value_int'], condition=Q(value_uuid=None), name='Documents_param_1c_unique_constraint_15'),
            UniqueConstraint(fields=['type', 'value_uuid'], condition=Q(value=None) & Q(value_boolean=None) & Q(value_float=None) & Q(value_int=None), name='Documents_param_1c_unique_constraint_16'),
            UniqueConstraint(fields=['type', 'value', 'value_uuid'], condition=Q(value_boolean=None) & Q(value_float=None) & Q(value_int=None), name='Documents_param_1c_unique_constraint_17'),
            UniqueConstraint(fields=['type', 'value_boolean', 'value_uuid'], condition=Q(value=None) & Q(value_float=None) & Q(value_int=None), name='Documents_param_1c_unique_constraint_18'),
            UniqueConstraint(fields=['type', 'value', 'value_boolean', 'value_uuid'], condition=Q(value_float=None) & Q(value_int=None), name='Documents_param_1c_unique_constraint_19'),
            UniqueConstraint(fields=['type', 'value_float', 'value_uuid'], condition=Q(value=None) & Q(value_boolean=None) & Q(value_int=None), name='Documents_param_1c_unique_constraint_20'),
            UniqueConstraint(fields=['type', 'value', 'value_float', 'value_uuid'], condition=Q(value_boolean=None) & Q(value_int=None), name='Documents_param_1c_unique_constraint_21'),
            UniqueConstraint(fields=['type', 'value_boolean', 'value_float', 'value_uuid'], condition=Q(value=None) & Q(value_int=None), name='Documents_param_1c_unique_constraint_22'),
            UniqueConstraint(fields=['type', 'value', 'value_boolean', 'value_float', 'value_uuid'], condition=Q(value_int=None), name='Documents_param_1c_unique_constraint_23'),
            UniqueConstraint(fields=['type', 'value_int', 'value_uuid'], condition=Q(value=None) & Q(value_boolean=None) & Q(value_float=None), name='Documents_param_1c_unique_constraint_24'),
            UniqueConstraint(fields=['type', 'value', 'value_int', 'value_uuid'], condition=Q(value_boolean=None) & Q(value_float=None), name='Documents_param_1c_unique_constraint_25'),
            UniqueConstraint(fields=['type', 'value_boolean', 'value_int', 'value_uuid'], condition=Q(value=None) & Q(value_float=None), name='Documents_param_1c_unique_constraint_26'),
            UniqueConstraint(fields=['type', 'value', 'value_boolean', 'value_int', 'value_uuid'], condition=Q(value_float=None), name='Documents_param_1c_unique_constraint_27'),
            UniqueConstraint(fields=['type', 'value_float', 'value_int', 'value_uuid'], condition=Q(value=None) & Q(value_boolean=None), name='Documents_param_1c_unique_constraint_28'),
            UniqueConstraint(fields=['type', 'value', 'value_float', 'value_int', 'value_uuid'], condition=Q(value_boolean=None), name='Documents_param_1c_unique_constraint_29'),
            UniqueConstraint(fields=['type', 'value_boolean', 'value_float', 'value_int', 'value_uuid'], condition=Q(value=None), name='Documents_param_1c_unique_constraint_30'),
            UniqueConstraint(fields=['type', 'value', 'value_boolean', 'value_float', 'value_int', 'value_uuid'], name='Documents_param_1c_unique_constraint_31'),
        ]
