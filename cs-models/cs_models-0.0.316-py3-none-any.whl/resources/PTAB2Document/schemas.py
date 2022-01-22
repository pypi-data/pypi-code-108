from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)

from cs_models.utils.utils import convert_string_to_datetime


def _pre_load_datetime_fields(in_data):
    date_fields = [
        'document_filing_date',
        'petitioner_grant_date',
        'respondent_grant_date',
    ]

    for date_field in date_fields:
        if date_field in in_data:
            if in_data[date_field] in ['-', None]:
                in_data[date_field] = None
            else:
                in_data[date_field] = convert_string_to_datetime(
                    date=in_data[date_field],
                    string_format='%m-%d-%Y',
                )

    return in_data


class PTAB2DocumentResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    document_category = fields.String()
    document_filing_date = fields.DateTime(allow_none=True)
    document_identifier = fields.String(required=True)
    document_name = fields.String(allow_none=True)
    document_number = fields.String(allow_none=True)
    document_size = fields.String(allow_none=True)
    document_title_text = fields.String(allow_none=True)
    document_type_name = fields.String(allow_none=True)
    filing_party_category = fields.String(allow_none=True)
    media_type_category = fields.String(allow_none=True)
    petitioner_application_number_text = fields.String(allow_none=True)
    petitioner_counsel_name = fields.String(allow_none=True)
    petitioner_grant_date = fields.DateTime(allow_none=True)
    petitioner_group_art_unit_number = fields.String(allow_none=True)
    petitioner_inventor_name = fields.String(allow_none=True)
    petitioner_party_name = fields.String(allow_none=True)
    petitioner_patent_number = fields.String(allow_none=True)
    petitioner_patent_owner_name = fields.String(allow_none=True)
    petitioner_technology_center_number = fields.String(allow_none=True)
    proceeding_number = fields.String(allow_none=True)
    proceeding_type_category = fields.String(allow_none=True)
    respondent_application_number_text = fields.String(allow_none=True)
    respondent_counsel_name = fields.String(allow_none=True)
    respondent_grant_date = fields.DateTime(allow_none=True)
    respondent_group_art_unit_number = fields.String(allow_none=True)
    respondent_inventor_name = fields.String(allow_none=True)
    respondent_party_name = fields.String(allow_none=True)
    respondent_patent_number = fields.String(allow_none=True)
    respondent_patent_owner_name = fields.String(allow_none=True)
    respondent_technology_center_number = fields.String(allow_none=True)
    subproceeding_type_category = fields.String(allow_none=True)
    file_id = fields.Integer(allow_none=True)
    has_smart_doc = fields.Boolean()
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def convert_string_to_datetime(self, in_data):
        return _pre_load_datetime_fields(in_data)


class PTAB2DocumentQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    document_identifier = fields.String()
    proceeding_number = fields.String()
    has_smart_doc = fields.Boolean()


class PTAB2DocumentPatchSchema(Schema):
    file_id = fields.Integer()
    has_smart_doc = fields.Boolean()
