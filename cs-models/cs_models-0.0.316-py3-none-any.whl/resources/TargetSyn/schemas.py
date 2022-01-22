from marshmallow import (
    Schema,
    fields,
    validate,
)


class TargetSynResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    synonym = fields.String(required=True)
    target_id = fields.Integer(required=True)
    updated_at = fields.DateTime()
