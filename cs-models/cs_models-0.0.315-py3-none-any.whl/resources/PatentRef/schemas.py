from marshmallow import (
    Schema,
    fields,
    validate,
)


class PatentRefResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    patent_id = fields.Integer(required=True)
    cited_by = fields.String(required=True, validate=not_blank)
    ref_title = fields.String(required=True, allow_none=True)
    year = fields.String(allow_none=True)
    updated_at = fields.DateTime()
