from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)
from ...utils.utils import pre_load_date_fields


class MergerOutboxResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    announcement_date = fields.DateTime(required=True)
    news_id = fields.Integer(required=True)
    target_sec_id = fields.Integer(allow_none=True)
    target_ous_id = fields.Integer(allow_none=True)
    acquirer_sec_id = fields.Integer(allow_none=True)
    acquirer_ous_id = fields.Integer(allow_none=True)
    deal_value = fields.Decimal(allow_none=True)
    type = fields.String(allow_none=True)
    offer_price = fields.Float(allow_none=True)
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
