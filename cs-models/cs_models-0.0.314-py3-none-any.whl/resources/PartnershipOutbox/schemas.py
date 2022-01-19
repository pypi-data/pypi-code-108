from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)
from ...utils.utils import pre_load_date_fields


class PartnershipOutboxResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    announcement_date = fields.DateTime(required=True)
    news_id = fields.Integer(required=True)
    partner_one_sec_id = fields.Integer(allow_none=True)
    partner_one_ous_id = fields.Integer(allow_none=True)
    partner_two_sec_id = fields.Integer(allow_none=True)
    partner_two_ous_id = fields.Integer(allow_none=True)
    deal_value = fields.Decimal(allow_none=True)
    type = fields.String(allow_none=True)
    note = fields.String(allow_none=True)
    updated_at = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['announcement_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format="%Y%m%dT%H%M%S",
        )
        return in_data
