from marshmallow import (
    Schema,
    fields,
    validate,
)


class ConditionNewswireResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    news_id = fields.Integer(required=True)
    condition_id = fields.Integer(required=True)
    score = fields.Float(required=True)
    updated_at = fields.DateTime()
