from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    ValidationError,
)
from ...utils.utils import pre_load_date_fields


class StreamResourceSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    id = fields.Integer(dump_only=True)
    date = fields.DateTime(required=True)
    resource_type = fields.String(required=True)
    intervention_id = fields.Integer(allow_none=True)
    condition_id = fields.Integer(allow_none=True)
    company_sec_id = fields.Integer(allow_none=True)
    company_ous_id = fields.Integer(allow_none=True)
    ptab2_proceeding_id = fields.Integer(allow_none=True)
    source_table = fields.String(required=True)
    source_table_id = fields.Integer(required=True)
    news_id = fields.Integer(allow_none=True)
    sec_filing_id = fields.Integer(allow_none=True)
    ptab2_document_id = fields.Integer(allow_none=True)
    pubmed_id = fields.Integer(allow_none=True)
    company_filing_id = fields.Integer(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def check_resource_info(self, in_data):
        if self._get_number_of_resource_fields(in_data) == 0:
            raise ValidationError('Provide at least one resource info')
        if self._get_number_of_source_fields(in_data) != 1:
            raise ValidationError('Provide only one source info')

    def _get_number_of_resource_fields(self, in_data):
        result = 0
        if 'intervention_id' in in_data:
            if in_data['intervention_id'] is not None:
                result += 1
        if 'condition_id' in in_data:
            if in_data['condition_id'] is not None:
                result += 1
        if 'company_sec_id' in in_data:
            if in_data['company_sec_id'] is not None:
                result += 1
        if 'company_ous_id' in in_data:
            if in_data['company_ous_id'] is not None:
                result += 1
        if 'ptab2_proceeding_id' in in_data:
            if in_data['ptab2_proceeding_id'] is not None:
                result += 1
        return result

    def _get_number_of_source_fields(self, in_data):
        result = 0
        if 'news_id' in in_data:
            if in_data['news_id'] is not None:
                result += 1
        if 'sec_filing_id' in in_data:
            if in_data['sec_filing_id'] is not None:
                result += 1
        if 'ptab2_document_id' in in_data:
            if in_data['ptab2_document_id'] is not None:
                result += 1
        if 'pubmed_id' in in_data:
            if in_data['pubmed_id'] is not None:
                result += 1
        if 'company_filing_id' in in_data:
            if in_data['company_filing_id'] is not None:
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
