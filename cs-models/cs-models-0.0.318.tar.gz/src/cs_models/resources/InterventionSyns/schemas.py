from marshmallow import (
    Schema,
    fields,
    validate,
)


class InterventionSynsResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    term = fields.String(validate=not_blank, required=True)
    nct_id = fields.String(validate=not_blank, required=True)
    intervention_id = fields.Integer()
    updated_at = fields.DateTime()
