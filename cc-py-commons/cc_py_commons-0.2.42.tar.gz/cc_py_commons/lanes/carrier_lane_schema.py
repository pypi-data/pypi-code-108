from cc_py_commons.lanes.lane_schema import LaneSchema
from marshmallow import fields, EXCLUDE, post_load
from cc_py_commons.schemas.camel_case_schema import CamelCaseSchema
from cc_py_commons.lanes.lane_schema import LaneSchema

class CarrierLaneSchema(CamelCaseSchema):
  class Meta:
      unknown = EXCLUDE
  
  carrierId: fields.UUID()
  laneDTO: fields.Nested(LaneSchema)
  hasBackhaulLane = fields.Boolean(allow_none=True)
  isBackhaulLane = fields.Boolean(allow_none=True)
  createBackhaulLanes = fields.Boolean(allow_none=True)
  deleted = fields.Boolean(allow_none=True)
  weeklyFrequency = fields.Integer(allow_none=True)
  runDaily = fields.Boolean(allow_none=True)
  monday = fields.Boolean(allow_none=True)
  tuesday = fields.Boolean(allow_none=True)
  wednesday = fields.Boolean(allow_none=True)
  thursday = fields.Boolean(allow_none=True)
  friday = fields.Boolean(allow_none=True)
  saturday = fields.Boolean(allow_none=True)
  sunday = fields.Boolean(allow_none=True)
  age = fields.Float(allow_none=True)
  rating = fields.Integer(allow_none=True)
  rate = fields.Integer(allow_none=True)
  rateUpdatedAt = fields.Date(allow_none=True)
  fromCarrier = fields.Boolean(allow_none=True)
  toBeReviewed = fields.Boolean(allow_none=True)