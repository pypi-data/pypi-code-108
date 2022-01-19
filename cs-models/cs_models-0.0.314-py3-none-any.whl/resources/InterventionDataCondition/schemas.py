from marshmallow import (
    Schema,
    fields,
    validate,
)


class InterventionDataConditionResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_data_id = fields.Integer(required=True)
    condition_id = fields.Integer(required=True)
    updated_at = fields.DateTime()
