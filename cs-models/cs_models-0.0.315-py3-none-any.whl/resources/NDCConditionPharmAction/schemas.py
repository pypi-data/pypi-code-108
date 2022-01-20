from marshmallow import (
    Schema,
    fields,
    validate,
)


class NDCConditionPharmActionResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    product_ndc = fields.String(validate=not_blank, required=True)
    name = fields.String(allow_none=True)
    rxcui = fields.String(validate=not_blank, required=True)
    condition_id = fields.Integer(required=True)
    pharm_action_id = fields.Integer(required=True)
    updated_at = fields.DateTime()
