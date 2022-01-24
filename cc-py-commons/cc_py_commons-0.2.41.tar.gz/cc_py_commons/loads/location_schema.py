from marshmallow import fields, EXCLUDE
from cc_py_commons.schemas.camel_case_schema import CamelCaseSchema

class LocationSchema(CamelCaseSchema):
  class Meta:
      unknown = EXCLUDE
      
  city = fields.String()
  state = fields.String()
  postcode = fields.String(allow_none=True)
  county = fields.String(allow_none=True) 
  country = fields.String(allow_none=True)
  latitude = fields.Float(allow_none=True)
  longitude = fields.Float(allow_none=True)
  