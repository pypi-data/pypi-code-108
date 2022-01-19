from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    ValidationError,
)

from ...utils.utils import pre_load_date_fields


class ClinicalDataOutboxResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    date = fields.DateTime(required=True)
    news_id = fields.Integer(allow_none=True)
    pubmed_id = fields.Integer(allow_none=True)
    intervention_id = fields.Integer(allow_none=True)
    condition_id = fields.Integer(allow_none=True)
    stage = fields.Integer(allow_none=True)
    updated_at = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['date']

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
                                  'pubmed_id, not both')

    def _get_number_of_source_fields(self, in_data):
        result = 0
        if 'news_id' in in_data:
            if in_data['news_id'] is not None:
                result += 1
        if 'pubmed_id' in in_data:
            if in_data['pubmed_id'] is not None:
                result += 1
        return result
