from marshmallow import (
    Schema,
    fields,
    validate,
)


class LicensingResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_id = fields.Integer(required=True)
    originator_subsidiary_id = fields.Integer(required=True)
    target_subsidiary_id = fields.Integer(required=True)
    type = fields.String(validate=not_blank, required=True)
    terms = fields.String(allow_none=True)
    is_deleted = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime()


class LicensingPatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')
    id = fields.Integer(required=True)
    is_deleted = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime()
