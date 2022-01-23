from marshmallow import (
    Schema,
    fields,
    validate,
)


class PubmedPMCResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    pubmed_id = fields.Integer(required=True)
    pmc_id = fields.String(required=True)
    updated_at = fields.DateTime()
