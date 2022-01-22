from marshmallow import (
    Schema,
    fields,
    validate,
)


class CatalystConceptResourceSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    id = fields.Integer(dump_only=True)
    concept_name = fields.String(required=True)
    relation = fields.String(required=True)
    property = fields.String(required=True)
    news_id = fields.Integer(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)
