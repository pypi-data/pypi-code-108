from marshmallow import (
    Schema,
    fields,
    validate,
)


class ViewInterventionNormModalityResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_norm_cui = fields.String(required=True)
    modality = fields.String(required=True)
    updated_at = fields.DateTime()
