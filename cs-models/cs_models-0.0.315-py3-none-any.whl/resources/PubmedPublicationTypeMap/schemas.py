from marshmallow import (
    Schema,
    fields,
    validate,
)


class PubmedPublicationTypeMapResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    pubmed_id = fields.Integer(required=True)
    publication_type_id = fields.Integer(required=True)
    processed = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime()
