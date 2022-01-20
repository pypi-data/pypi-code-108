from marshmallow import (
    Schema,
    fields,
    validate,
)


class ModalityResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    modality = fields.String(required=True)
    updated_at = fields.DateTime()
