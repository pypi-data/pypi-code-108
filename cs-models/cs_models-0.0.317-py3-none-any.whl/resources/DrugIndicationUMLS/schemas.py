from marshmallow import (
    Schema,
    fields,
    validate,
)


class DrugIndicationUMLSResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    set_id = fields.String(validate=not_blank, required=True)
    cui = fields.String(required=True)
    preferred_name = fields.String(allow_none=True)
    score = fields.Integer(allow_none=True)
    final_mapping = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime()
