from marshmallow import (
    Schema,
    fields,
    validate,
)


class ConditionSynsResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    term = fields.String(validate=not_blank, required=True)
    disease_id = fields.String(validate=not_blank, required=True)
    disease_name = fields.String(validate=not_blank, required=True)
    updated_at = fields.DateTime()
