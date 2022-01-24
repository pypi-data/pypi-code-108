from marshmallow import fields, EXCLUDE, post_load
from cc_py_commons.schemas.camel_case_schema import CamelCaseSchema
from cc_py_commons.bids.bid import Bid
from cc_py_commons.bids.bid_history_schema import BidHistorySchema

class BidSchema(CamelCaseSchema):
  class Meta:
    unknown = EXCLUDE

  id = fields.UUID()
  quote_id = fields.UUID()
  carrier_id = fields.UUID()
  receipt_id = fields.String(allow_none=True)
  amount = fields.Integer()
  estimated_days = fields.Integer()
  notes = fields.String(allow_none=True)
  match_score = fields.Float(allow_none=True)
  status_id = fields.UUID()
  pickup_date = fields.Date()
  delivery_date = fields.Date()
  decline_reason = fields.String(allow_none=True)
  bid_histories = fields.List(fields.Nested(BidHistorySchema), allow_none=True)
  origin_deadhead = fields.Float(allow_none=True)
  porus_truck_id = fields.UUID(allow_none=True)
  truck_lane_id = fields.UUID(allow_none=True)
  distance = fields.Float(allow_none=True)
  origin_city = fields.String()
  origin_state = fields.String()
  origin_zip = fields.String()
  dest_city = fields.String()
  dest_state = fields.String()
  dest_zip = fields.String()

  @post_load
  def make_bid(self, data, **kwargs):
      return Bid(**data)
   