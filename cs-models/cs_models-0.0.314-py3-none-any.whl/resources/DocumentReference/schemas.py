from marshmallow import (
    Schema,
    fields,
    validate,
)


class DocumentReferenceResourceSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    id = fields.Integer(dump_only=True)
    ptab2_document_id = fields.Integer(required=True)
    type = fields.String(required=True)
    value = fields.String(required=True)

    federal_case_headline = fields.String(allow_none=True)
    federal_case_number = fields.String(allow_none=True)
    link = fields.String(allow_none=True)
    federal_case_file_id = fields.Integer(allow_none=True)
    pages = fields.String(required=True)

    updated_at = fields.DateTime(dump_only=True)


class DocumentReferenceQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    id = fields.Integer()
    ptab2_document_id = fields.Integer()
    type = fields.String()
    value = fields.String()
    federal_case_number = fields.String()
    link = fields.String()
    pages = fields.String()


class DocumentReferencePatchSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    federal_case_headline = fields.String(allow_none=True)
    federal_case_number = fields.String(allow_none=True)
    link = fields.String(allow_none=True)
    federal_case_file_id = fields.Integer(allow_none=True)
    pages = fields.String(allow_none=False)
