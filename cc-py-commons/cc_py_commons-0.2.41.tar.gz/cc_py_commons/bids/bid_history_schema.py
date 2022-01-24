from marshmallow import fields, EXCLUDE, post_load
from cc_py_commons.schemas.camel_case_schema import CamelCaseSchema

class BidHistorySchema(CamelCaseSchema):
  class Meta:
    unknown = EXCLUDE

  id = fields.UUID()
  bid_id = fields.UUID()
  source_type = fields.String(allow_none=True)
  source_id = fields.Integer(allow_none=True)
  amount = fields.Integer()
  carrier_id = fields.UUID(allow_none=True)
  pickup_date = fields.Date()
  delivery_date = fields.Date()
