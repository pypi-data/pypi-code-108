from marshmallow import (
    Schema,
    fields,
    validate,
)


class ViewInterventionNormTargetResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_norm_cui = fields.String(required=True)
    target_id = fields.Integer(required=True)
    updated_at = fields.DateTime()
