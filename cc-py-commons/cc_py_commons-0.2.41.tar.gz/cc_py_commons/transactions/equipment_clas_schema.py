from marshmallow import fields, EXCLUDE, post_load

from cc_py_commons.schemas.camel_case_schema import CamelCaseSchema
from cc_py_commons.transactions.equipment_class import EquipmentClass

class EquipmentClassSchema(CamelCaseSchema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String()
    active = fields.Boolean(default=False)

    @post_load
    def classify(self, data, **kwargs):
        return EquipmentClass(**data)