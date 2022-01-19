from marshmallow import (
    Schema,
    fields,
    validate,
)


class PatentIFWResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    patent_id = fields.Integer(required=True)
    document_identifier = fields.String(required=True, validate=not_blank)
    document_code = fields.String()
    document_description = fields.String()
    direction_category = fields.String()
    official_date = fields.DateTime()
    total_pages = fields.Integer()
    updated_at = fields.DateTime()
