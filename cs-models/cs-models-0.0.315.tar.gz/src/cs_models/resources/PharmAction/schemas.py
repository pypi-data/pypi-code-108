from marshmallow import (
    Schema,
    fields,
    validate,
)


class PharmActionResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    pharm_action_id = fields.String(validate=not_blank, required=True)
    pharm_action = fields.String(validate=not_blank, required=True)
    pharm_action_type = fields.String()
    updated_at = fields.DateTime()
