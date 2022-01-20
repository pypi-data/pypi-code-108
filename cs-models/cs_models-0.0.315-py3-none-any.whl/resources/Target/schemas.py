from marshmallow import (
    Schema,
    fields,
    validate,
)


class TargetResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    cui = fields.String(required=True)
    name = fields.String(required=True)
    symbol = fields.String(required=True)
    bio_type = fields.String(allow_none=True)
    pathways = fields.String(allow_none=True)
    updated_at = fields.DateTime()
