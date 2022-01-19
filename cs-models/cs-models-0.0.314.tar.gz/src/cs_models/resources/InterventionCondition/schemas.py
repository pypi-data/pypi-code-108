from marshmallow import (
    Schema,
    fields,
    validate,
)


class InterventionConditionResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_id = fields.Integer(required=True)
    condition_id = fields.Integer(required=True)
    stage = fields.Integer(allow_none=True)
    geography = fields.String(allow_none=True)
    line = fields.Integer(allow_none=True)
    discontinued = fields.Boolean(allow_none=True)
    is_deleted = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime()
