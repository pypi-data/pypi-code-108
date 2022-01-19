from marshmallow import (
    Schema,
    fields,
    validate,
)


class InterventionDataRawResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    source_type = fields.String(required=True)
    source_id = fields.Integer(required=True)
    insight_type = fields.String(required=True)
    insight_name = fields.String()
    updated_at = fields.DateTime()
