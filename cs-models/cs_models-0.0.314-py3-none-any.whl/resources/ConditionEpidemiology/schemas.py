from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    ValidationError,
)
from ...utils.utils import pre_load_date_fields


class ConditionEpidemiologyResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    source_date = fields.DateTime(required=True)
    source_title = fields.String(required=True)
    source_name = fields.String(required=True)
    source_table = fields.String(required=True)
    source_table_id = fields.Integer(required=True)
    pubmed_id = fields.Integer(allow_none=True)
    news_id = fields.Integer(allow_none=True)
    measure = fields.String(required=True)
    geographic_area = fields.String(allow_none=True)
    snippet = fields.String(required=True)
    statistic = fields.Float(allow_none=True)
    statistic_text = fields.String(allow_none=True)
    year = fields.String(allow_none=True)
    population_type = fields.String(allow_none=True)
    updated_at = fields.DateTime()

    @pre_load
    def check_resource_info(self, in_data):
        if self._get_number_of_source_fields(in_data) != 1:
            raise ValidationError('Provide only one source info')

    def _get_number_of_source_fields(self, in_data):
        result = 0
        if 'news_id' in in_data:
            if in_data['news_id'] is not None:
                result += 1
        if 'pubmed_id' in in_data:
            if in_data['pubmed_id'] is not None:
                result += 1
        return result

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format="%Y%m%dT%H%M%S",
        )
        return in_data
