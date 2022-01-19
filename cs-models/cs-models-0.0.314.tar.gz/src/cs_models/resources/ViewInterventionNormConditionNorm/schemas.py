from marshmallow import (
    Schema,
    fields,
    validate,
)


class ViewInterventionNormConditionNormResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_norm_cui = fields.String(required=True)
    condition_norm_cui = fields.String(required=True)
    condition_norm_cui_name = fields.String(required=True)
    updated_at = fields.DateTime()
