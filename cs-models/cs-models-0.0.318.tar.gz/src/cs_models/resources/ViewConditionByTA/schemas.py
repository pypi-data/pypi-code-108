from marshmallow import (
    Schema,
    fields,
    validate,
)


class ViewConditionByTAResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    ta_id = fields.Integer(required=True)
    hlt_name = fields.String(required=True)
    disease_name = fields.String(required=True)
    disease_id = fields.String(required=True)
    updated_at = fields.DateTime()
