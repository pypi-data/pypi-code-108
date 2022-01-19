from marshmallow import (
    Schema,
    fields,
    validate,
)


class TableOutboxResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    sec_filing_id = fields.Integer(required=True)
    table_number = fields.Integer(required=True)
    table_html = fields.String(required=True)
    table_preceding_info = fields.String(required=True)
    updated_at = fields.DateTime()
