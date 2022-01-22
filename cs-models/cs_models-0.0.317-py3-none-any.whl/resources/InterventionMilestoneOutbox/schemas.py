from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    ValidationError,
)
from ...utils.utils import pre_load_date_fields


class InterventionMilestoneOutboxResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    date = fields.DateTime(required=True)
    news_id = fields.Integer(allow_none=True)
    sec_filing_id = fields.Integer(allow_none=True)
    note = fields.String(validate=not_blank, required=True)
    intervention_id = fields.Integer(allow_none=True)
    condition_id = fields.Integer(allow_none=True)
    start_date = fields.DateTime(allow_none=True)
    end_date = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['date', 'start_date', 'end_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format="%Y%m%dT%H%M%S",
        )
        return in_data

    @pre_load
    def check_source_ids(self, in_data):
        if self._get_number_of_source_fields(in_data) != 1:
            raise ValidationError('Provide either news_id or '
                                  'sec_id, not both')

    def _get_number_of_source_fields(self, in_data):
        result = 0
        if 'news_id' in in_data:
            if in_data['news_id'] is not None:
                result += 1
        if 'sec_filing_id' in in_data:
            if in_data['sec_filing_id'] is not None:
                result += 1
        return result

