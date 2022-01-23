from marshmallow import (
    Schema,
    fields,
    validate,
)


class ConditionNormTAResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    condition_norm_cui = fields.String(required=True)
    therapeutic_area_id = fields.Integer(required=True)
    updated_at = fields.DateTime()
