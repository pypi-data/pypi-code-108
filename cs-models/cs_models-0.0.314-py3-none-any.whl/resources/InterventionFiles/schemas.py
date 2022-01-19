from marshmallow import (
    Schema,
    fields,
    validate,
)


class InterventionFileResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_id = fields.Integer(required=True)
    file_id = fields.Integer(required=True)
    type = fields.String(required=True)
    orig_file_url = fields.String(allow_none=True)
    is_deleted = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime()
