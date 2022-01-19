from marshmallow import (
    Schema,
    fields,
    validate,
)


class SubsidiarySponsorMappingResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    sponsor_id = fields.Integer(required=True)
    sponsor_name = fields.String(required=True, validate=not_blank)
    lead_or_collaborator = fields.String()
    subsidiary_id = fields.Integer(required=True)
    updated_at = fields.DateTime(dump_only=True)


class SubsidiarySponsorMappingQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    sponsor_id = fields.Integer()
    sponsor_name = fields.String(validate=not_blank)
    lead_or_collaborator = fields.String()
    subsidiary_id = fields.Integer()
