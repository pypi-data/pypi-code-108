from marshmallow import (
    Schema,
    fields,
    validate,
)


class BiomarkerSynResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    biomarker_id = fields.String(required=True)
    synonym = fields.String(required=True)
    updated_at = fields.DateTime()
