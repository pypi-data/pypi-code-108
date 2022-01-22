from marshmallow import (
    Schema,
    fields,
    validate,
)


class SalesResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    sec_filing_id = fields.Integer(required=True)
    table_html_file_id = fields.Integer(allow_none=True)
    table_number = fields.Integer(required=True)
    table_preceding_info = fields.String(allow_none=True)
    updated_at = fields.DateTime()
