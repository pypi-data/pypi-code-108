from marshmallow import (
    Schema,
    fields,
    validate,
)


class InterventionNCTResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_id = fields.Integer(required=True)
    nct_id = fields.String(required=True)
    match_score = fields.Float(required=True)
    updated_at = fields.DateTime()

