from marshmallow import (
    Schema,
    fields,
    validate,
)


class ConditionNormResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    condition_id = fields.Integer(required=True)
    condition_norm_cui = fields.String(required=True)
    condition_norm_cui_name = fields.String(required=True)
    condition_norm_cui_broader = fields.String(required=True)
    condition_norm_cui_name_broader = fields.String(required=True)
    condition_norm_name = fields.String(required=True)
    updated_at = fields.DateTime()
