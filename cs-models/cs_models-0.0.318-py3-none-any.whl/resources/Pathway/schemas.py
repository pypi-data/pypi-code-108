from marshmallow import (
    Schema,
    fields,
    validate,
)


class PathwayResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    reactome_pathway_id = fields.String(required=True)
    reactome_pathway_name = fields.String(required=True)
    reactome_pathway_type = fields.String(required=True)
    updated_at = fields.DateTime()
