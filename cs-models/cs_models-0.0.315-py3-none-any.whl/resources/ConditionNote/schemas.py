from marshmallow import (
    Schema,
    fields,
    validate,
)


class ConditionNoteResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    condition_id = fields.Integer(required=True)
    type = fields.String(validate=not_blank, required=True)
    note = fields.String(validate=not_blank, required=True)
    source = fields.String()
    updated_at = fields.DateTime()
