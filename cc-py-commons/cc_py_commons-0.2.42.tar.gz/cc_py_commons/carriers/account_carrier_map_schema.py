from marshmallow import fields, EXCLUDE, post_load
from cc_py_commons.schemas.camel_case_schema import CamelCaseSchema
from cc_py_commons.carriers.contact_schema import ContactSchema
from cc_py_commons.carriers.account_carrier_map import AccountCarrierMap
class AccountCarrierMapSchema(CamelCaseSchema):
  class Meta:
    unknown = EXCLUDE

  account_id = fields.Integer()
  customer_code = fields.String(allow_none=True)
  carrier_id = fields.UUID()
  status = fields.String(allow_none=True)
  warmup_email_sent_at = fields.Date(allow_none=True)

  @post_load
  def make_bid(self, data, **kwargs):
      return AccountCarrierMap(**data)  