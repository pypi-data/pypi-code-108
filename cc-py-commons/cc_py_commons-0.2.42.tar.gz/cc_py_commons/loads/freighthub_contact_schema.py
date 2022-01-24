from marshmallow import fields, EXCLUDE
from cc_py_commons.schemas.camel_case_schema import CamelCaseSchema

class FreightHubContactSchema(CamelCaseSchema):
  class Meta:
      unknown = EXCLUDE
        
  contact_name = fields.String()
  contact_phone = fields.String(allow_none=True)
  contact_fax = fields.String(allow_none=True)
  contact_email = fields.String()
  company_name = fields.String()
  user_id = fields.String(allow_none=True)