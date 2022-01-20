from marshmallow import (
    Schema,
    fields,
    validate,
)


class DesignationOutboxResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_condition_id = fields.Integer(allow_none=True)
    designation = fields.String(validate=not_blank, required=True)
    designation_text = fields.String(validate=not_blank)
    news_id = fields.Integer(required=True)
    updated_at = fields.DateTime()
