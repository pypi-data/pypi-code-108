from marshmallow import (
    Schema,
    fields,
    validate,
)


class InterventionTypeResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_id = fields.Integer(required=True)
    route = fields.String(allow_none=True)
    modality = fields.String(allow_none=True)
    dosage_form = fields.String(allow_none=True)
    combination_therapy = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime()
