from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)
from ...utils.utils import pre_load_date_fields


class PacerCaseResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    case_no = fields.String(required=True, validate=not_blank)
    court_id = fields.String(required=True, validate=not_blank)
    pacer_case_external_id = fields.String(required=True, validate=not_blank)
    cause = fields.String()
    county = fields.String()
    defendant = fields.String()
    disposition = fields.String()
    filed_date = fields.DateTime(allow_none=True)
    flags = fields.String()
    jurisdiction = fields.String()
    lead_case = fields.String()
    nature_of_suit = fields.String()
    office = fields.String()
    plaintiff = fields.String()
    related_case = fields.String()
    terminated_date = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['filed_date', 'terminated_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%m/%d/%Y',
        )
        return in_data


class PacerCaseQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    ids = fields.List(fields.Integer())
    case_no = fields.String()
    court_id = fields.String()
    pacer_case_external_id = fields.String()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['filed_date', 'terminated_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%m/%d/%Y',
        )
        return in_data


class PacerCasePatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    case_no = fields.String(validate=not_blank)
    court_id = fields.String(required=True, validate=not_blank)
    pacer_case_external_id = fields.String(required=True, validate=not_blank)
    cause = fields.String()
    county = fields.String()
    defendant = fields.String()
    disposition = fields.String()
    filed_date = fields.DateTime()
    flags = fields.String()
    jurisdiction = fields.String()
    lead_case = fields.String()
    nature_of_suit = fields.String()
    office = fields.String()
    plaintiff = fields.String()
    related_case = fields.String()
    terminated_date = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['filed_date', 'terminated_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%m/%d/%Y',
        )
        return in_data
