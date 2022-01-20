from marshmallow import (
    Schema,
    fields,
    validate,
)


class SponsorResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(required=True)
    nct_id = fields.String()
    agency_class = fields.String()
    lead_or_collaborator = fields.String()
    name = fields.String()


class SponsorQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')
    id = fields.Integer()
    name = fields.String()
