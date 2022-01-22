from marshmallow import (
    Schema,
    fields,
    validate,
)


class InterventionNormResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_id = fields.Integer(required=True)
    norm_cui = fields.String(validate=not_blank, required=True)
    norm_cui_name = fields.String(validate=not_blank, required=True)
    is_deleted = fields.Boolean(allow_none=True)
    is_combination_element = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime()


class InterventionNormUpdateSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    intervention_id = fields.Integer(required=True)
    norm_cui = fields.String(validate=not_blank, required=True)
    is_deleted = fields.Boolean(allow_none=True)
    is_combination_element = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime()
