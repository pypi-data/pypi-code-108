from marshmallow import fields, EXCLUDE, post_load

from cc_py_commons.schemas.camel_case_schema import CamelCaseSchema
from cc_py_commons.transactions.equipment_class import EquipmentClass
from cc_py_commons.transactions.equipment_mapping import EquipmentMapping

class EquipmentClassSchema(CamelCaseSchema):
    class Meta:
        unknown = EXCLUDE

    equipment_class = fields.Nested(EquipmentClass)
    mapped_text = fields.String()

    @post_load
    def classify(self, data, **kwargs):
        return EquipmentClass(**data)        