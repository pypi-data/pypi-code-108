from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    ValidationError,
)
from ...utils.utils import pre_load_date_fields


class InterventionDataResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    source_type = fields.String()
    date = fields.DateTime(allow_none=True)
    news_id = fields.Integer(allow_none=True)
    pubmed_id = fields.Integer(allow_none=True)
    file_id = fields.Integer(allow_none=True)
    title = fields.String(allow_none=True)
    orig_file_url = fields.String(allow_none=True)
    is_deleted = fields.Boolean(allow_none=True)
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
        if 'file_id' in in_data:
            if in_data['file_id'] is not None:
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
