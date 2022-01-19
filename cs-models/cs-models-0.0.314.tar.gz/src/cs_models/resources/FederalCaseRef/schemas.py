from marshmallow import (
    Schema,
    fields,
    validate,
)


class FederalCaseRefResourceSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    id = fields.Integer(dump_only=True)
    case_name = fields.String(required=True)
    volume = fields.Integer(required=True)
    reporter_type = fields.String(required=True)
    page = fields.Integer(required=True)
    title = fields.String(required=True)
    link = fields.String(required=True)
    federal_case_file_id = fields.Integer(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)
