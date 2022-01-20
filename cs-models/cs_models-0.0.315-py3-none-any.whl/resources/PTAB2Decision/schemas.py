from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)

from ...utils.utils import convert_string_to_datetime


def _pre_load_datetime_fields(in_data):
    date_fields = [
        'decision_date',
        'petitioner_grant_date',
        'respondent_grant_date',
    ]

    for date_field in date_fields:
        if date_field in in_data:
            if(
                in_data[date_field] == '-' or
                in_data[date_field] is None
            ):
                in_data[date_field] = None
            else:
                in_data[date_field] = convert_string_to_datetime(
                    date=in_data[date_field],
                    string_format='%m-%d-%Y',
                )

    return in_data


class PTAB2DecisionResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    board_rulings = fields.String(allow_none=True)
    decision_date = fields.DateTime(allow_none=True)
    decision_type_category = fields.String(allow_none=True)
    document_identifier = fields.String(allow_none=True)
    document_name = fields.String(allow_none=True)
    identifier = fields.String(required=True)
    issue_type = fields.String(allow_none=True)
    petitioner_application_number_text = fields.String(allow_none=True)
    petitioner_counsel_name = fields.String(allow_none=True)
    petitioner_grant_date = fields.DateTime(allow_none=True)
    petitioner_group_art_unit_number = fields.String(allow_none=True)
    petitioner_inventor_name = fields.String(allow_none=True)
    petitioner_party_name = fields.String(allow_none=True)
    petitioner_patent_number = fields.String(allow_none=True)
    petitioner_patent_owner_name = fields.String(allow_none=True)
    petitioner_technology_center_number = fields.String(allow_none=True)
    proceeding_number = fields.String(required=True)
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
    subdecision_type_category = fields.String(allow_none=True)
    subproceeding_type_category = fields.String(allow_none=True)
    claim_invalidation_status = fields.String(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def convert_string_to_datetime(self, in_data):
        return _pre_load_datetime_fields(in_data)


class PTAB2DecisionPatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    board_rulings = fields.String(allow_none=True)
    decision_date = fields.DateTime(allow_none=True)
    decision_type_category = fields.String(allow_none=True)
    document_identifier = fields.String(allow_none=True)
    document_name = fields.String(allow_none=True)
    identifier = fields.String(required=True)
    issue_type = fields.String(allow_none=True)
    petitioner_application_number_text = fields.String(allow_none=True)
    petitioner_counsel_name = fields.String(allow_none=True)
    petitioner_grant_date = fields.DateTime(allow_none=True)
    petitioner_group_art_unit_number = fields.String(allow_none=True)
    petitioner_inventor_name = fields.String(allow_none=True)
    petitioner_party_name = fields.String(allow_none=True)
    petitioner_patent_number = fields.String(allow_none=True)
    petitioner_patent_owner_name = fields.String(allow_none=True)
    petitioner_technology_center_number = fields.String(allow_none=True)
    proceeding_number = fields.String(required=True)
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
    subdecision_type_category = fields.String(allow_none=True)
    subproceeding_type_category = fields.String(allow_none=True)
    claims_invalidation_status = fields.String(allow_none=True)


class PTAB2DecisionQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    identifier = fields.String()
