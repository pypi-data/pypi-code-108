from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)
from ...utils.utils import pre_load_date_fields


class CTProductsViewResourceSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    id = fields.Integer(dump_only=True)
    news_id = fields.Integer(required=True)
    news_date = fields.DateTime(required=True)
    intervention_name = fields.String(allow_none=True)
    nct_id = fields.String(allow_none=True)
    brief_title = fields.String(allow_none=True)
    study_status = fields.String(allow_none=True)
    study_start_date = fields.DateTime(allow_none=True)
    phase = fields.String(allow_none=True)
    company = fields.String(allow_none=True)
    sponsors = fields.String(allow_none=True)
    pharm_action = fields.String(allow_none=True)
    intervention_type = fields.String(allow_none=True)
    conditions = fields.String(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['news_date', 'study_start_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%Y-%m-%d',
        )
        return in_data
