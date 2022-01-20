from marshmallow import (
    Schema,
    fields,
    validate,
)


class BiomarkerResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    cui = fields.String(required=True)
    type = fields.String(required=True)
    approved_name = fields.String(required=True)
    approved_symbol = fields.String(allow_none=True)
    updated_at = fields.DateTime()
