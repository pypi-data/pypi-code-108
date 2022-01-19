from marshmallow import (
    Schema,
    fields,
    validate,
)


class TherapeuticAreaResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    name = fields.String(validate=not_blank, required=True)
    updated_at = fields.DateTime()
