from marshmallow import (
    Schema,
    fields,
    validate,
)


class ViewDealInterventionResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    deal_id = fields.Integer(required=True)
    intervention_id = fields.Integer(required=True)
    updated_at = fields.DateTime()
