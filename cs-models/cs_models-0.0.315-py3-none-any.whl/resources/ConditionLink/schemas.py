from marshmallow import (
    Schema,
    fields,
    validate,
)


class ConditionLinkResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    condition_id = fields.Integer(required=True)
    sibling_condition_id = fields.Integer(required=True)
    updated_at = fields.DateTime()
