from marshmallow import fields, EXCLUDE, post_load
from cc_py_commons.schemas.camel_case_schema import CamelCaseSchema
from cc_py_commons.loads.equipment import Equipment

class EquipmentSchema(CamelCaseSchema):
  class Meta:
      unknown = EXCLUDE
  
  id = fields.UUID()
  name = fields.String()

  @post_load
  def make_load(self, data, **kwargs):
      return Equipment(**data)  