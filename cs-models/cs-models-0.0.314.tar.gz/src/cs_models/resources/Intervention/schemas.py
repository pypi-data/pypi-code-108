from marshmallow import (
    Schema,
    fields,
    validate,
)


class InterventionResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_uid = fields.String(validate=not_blank, required=True)
    marketing_category = fields.String(allow_none=True)
    preferred_term = fields.String(validate=not_blank, required=True)
    intervention_type = fields.String(allow_none=True)
    intervention_url = fields.String(allow_none=True)
    discontinued = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime()
