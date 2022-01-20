from marshmallow import (
    Schema,
    fields,
    validate,
)


class NCTIdSubsidiaryResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    nct_id = fields.String(validate=not_blank, required=True)
    subsidiary_id = fields.Integer(required=True)
    lead_or_collaborator = fields.String()
    updated_at = fields.DateTime()
