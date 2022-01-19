from marshmallow import (
    Schema,
    fields,
    validate,
)


class InterventionNDCResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_id = fields.Integer(required=True)
    product_ndc = fields.String(required=True)
    match_type = fields.String(required=True)
    match_score = fields.Float(required=True)
    updated_at = fields.DateTime()

