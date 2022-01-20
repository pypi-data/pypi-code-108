from marshmallow import (
    Schema,
    fields,
    validate,
)


class InterventionRelsResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_id_1 = fields.Integer(required=True)
    intervention_id_2 = fields.Integer(required=True)
    relation = fields.String(validate=not_blank, required=True)
    is_deleted = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime()
