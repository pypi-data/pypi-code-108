from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    ValidationError,
)
from ...utils.utils import pre_load_date_fields


class EventResourceSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    id = fields.Integer(dump_only=True)
    date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
    event_type = fields.String(required=True)
    description = fields.String(required=True)
    products = fields.String(allow_none=True)
    company_sec_id = fields.Integer(allow_none=True)
    company_ous_id = fields.Integer(allow_none=True)
    news_id = fields.Integer(allow_none=True)
    sec_filing_id = fields.Integer(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def check_company_info(self, in_data):
        if self._get_number_of_company_fields(in_data) > 1:
            raise ValidationError('Provide either company_sec_id or '
                                  'company_ous_id, not both')

    def _get_number_of_company_fields(self, in_data):
        result = 0
        if 'company_sec_id' in in_data:
            if in_data['company_sec_id'] is not None:
                result += 1
        if 'company_ous_id' in in_data:
            if in_data['company_ous_id'] is not None:
                result += 1
        return result

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['date', 'end_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format="%Y%m%dT%H%M%S",
        )
        return in_data
