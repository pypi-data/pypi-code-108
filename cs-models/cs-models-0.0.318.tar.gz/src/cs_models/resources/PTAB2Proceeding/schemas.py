from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)

from ...utils.utils import pre_load_date_fields


class PTAB2ProceedingResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    accorded_filing_date = fields.DateTime(allow_none=True)
    max_document_date = fields.DateTime(allow_none=True)
    decision_date = fields.DateTime(allow_none=True)
    institution_decision_date = fields.DateTime(allow_none=True)
    petitioner_application_number_text = fields.String(allow_none=True)
    petitioner_counsel_name = fields.String(allow_none=True)
    petitioner_grant_date = fields.DateTime(allow_none=True)
    petitioner_group_art_unit_number = fields.String(allow_none=True)
    petitioner_inventor_name = fields.String(allow_none=True)
    petitioner_party_name = fields.String(allow_none=True)
    petitioner_patent_number = fields.String(allow_none=True)
    petitioner_patent_owner_name = fields.String(allow_none=True)
    petitioner_technology_center_number = fields.String(allow_none=True)
    proceeding_filing_date = fields.DateTime(allow_none=True)
    proceeding_last_modified_date = fields.DateTime(allow_none=True)
    proceeding_number = fields.String(required=True)
    proceeding_status_category = fields.String(allow_none=True)
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
    proceeding_status = fields.String(allow_none=True)
    appealed = fields.Boolean(allow_none=True)
    respondent_subsidiary_id = fields.Integer(allow_none=True)
    petitioner_subsidiary_id = fields.Integer(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = [
            'accorded_filing_date',
            'decision_date',
            'institution_decision_date',
            'petitioner_grant_date',
            'proceeding_filing_date',
            'proceeding_last_modified_date',
            'respondent_grant_date',
            'max_document_date',
        ]

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%m-%d-%Y',
        )
        return in_data


class PTAB2ProceedingQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    proceeding_number = fields.String()
