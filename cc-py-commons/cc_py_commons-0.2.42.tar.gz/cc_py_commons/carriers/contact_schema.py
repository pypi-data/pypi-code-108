from dataclasses import MISSING
from marshmallow import fields, EXCLUDE, post_load
from cc_py_commons.schemas.camel_case_schema import CamelCaseSchema
from cc_py_commons.carriers.contact import Contact
class ContactSchema(CamelCaseSchema):
  class Meta:
    unknown = EXCLUDE

  id = fields.UUID(allow_none=True)
  carrier_id = fields.UUID(allow_none=True)
  first_name = fields.String()
  last_name = fields.String(allow_none=True)
  phone = fields.String(allow_none=True)
  email_address = fields.Email()
  mobile = fields.String(allow_none=True)
  primary_contact = fields.Boolean(allow_none=True, missgin=False)

  @post_load
  def make_bid(self, data, **kwargs):
      return Contact(**data)  