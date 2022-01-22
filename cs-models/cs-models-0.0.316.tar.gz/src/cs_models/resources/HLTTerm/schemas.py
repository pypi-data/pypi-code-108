from marshmallow import (
    Schema,
    fields,
    validate,
)


class HLTTermResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    hlt_code = fields.String(required=True)
    hlt_name = fields.String(required=True)
    type = fields.String(required=True)
    updated_at = fields.DateTime()
