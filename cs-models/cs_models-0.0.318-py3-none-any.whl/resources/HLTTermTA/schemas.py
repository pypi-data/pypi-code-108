from marshmallow import (
    Schema,
    fields,
    validate,
)


class HLTTermTAResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    hlt_id = fields.Integer(required=True)
    therapeutic_area_id = fields.Integer(required=True)
    updated_at = fields.DateTime()
