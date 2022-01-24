from cc_py_commons.lanes.lane import Lane
from marshmallow import fields, EXCLUDE, post_load
from cc_py_commons.schemas.camel_case_schema import CamelCaseSchema
from cc_py_commons.carriers.contact_schema import ContactSchema
from cc_py_commons.carriers.account_carrier_map_schema import AccountCarrierMapSchema
from cc_py_commons.lanes.lane_schema import LaneSchema
from cc_py_commons.carriers.carrier import Carrier
class CarrierSchema(CamelCaseSchema):
  class Meta:
    unknown = EXCLUDE

  id = fields.UUID(allow_none=True)
  mc = fields.String(allow_none=True)
  dot = fields.String(allow_none=True)
  customer_code = fields.String(allow_none=True)
  business_name = fields.String()
  doing_business_as = fields.String(allow_none=True)
  address1 = fields.String(allow_none=True)
  city = fields.String(allow_none=True)
  state = fields.String(allow_none=True)
  postcode = fields.String(allow_none=True)
  country = fields.String(allow_none=True)
  latitude = fields.Float(allow_none=True)
  longitude = fields.Float(allow_none=True)
  qualified = fields.Boolean()
  drivers = fields.Integer(allow_none=True)
  active = fields.Boolean()
  active_checked_on = fields.Date()
  power_units = fields.Integer(allow_none=True)
  credit_score = fields.Integer(allow_none=True)
  days_to_pay = fields.Integer(allow_none=True)
  needs_review = fields.Boolean(allow_none=True)
  is_private = fields.Boolean()
  customer_count = fields.Integer(allow_none=True)
  dispatch_service = fields.Boolean(allow_none=True)
  default_trailer_type = fields.String(allow_none=True)
  carrier_last_fmcsa_update = fields.Date(allow_none=True)
  hazmat = fields.Boolean()
  hm_flag = fields.Boolean()
  mcs_150_date = fields.Date(allow_none=True)
  mcs_150_mileage = fields.Integer(allow_none=True)
  mcs_150_mileage_year = fields.Integer(allow_none=True)
  fmcsa_date_added = fields.Date(allow_none=True)
  fmcsa_oic_state = fields.String(allow_none=True)
  in_network = fields.Boolean()
  last_reviewed = fields.Date(allow_none=True)
  internal_remarks = fields.String(allow_none=True)
  contact_count = fields.Integer(allow_none=True)
  not_reached_count = fields.Integer(allow_none=True)
  not_reached_count_first_updated_at = fields.Date()
  lane_count = fields.Integer(allow_none=True)
  has_teams = fields.Boolean()
  contact = fields.Nested(ContactSchema, allow_none=True)
  account_carrier_maps = fields.List(fields.Nested(AccountCarrierMapSchema))
  lanes = fields.List(fields.Nested(LaneSchema))
  equipment_preferences = fields.List(fields.String)
  
  @post_load
  def make_bid(self, data, **kwargs):
      return Carrier(**data)
