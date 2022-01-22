from marshmallow import (
    Schema,
    fields,
    validate,
)


class HLTPTMapResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    hlt_id = fields.Integer(required=True)
    pt_code = fields.String(required=True)
    updated_at = fields.DateTime()
