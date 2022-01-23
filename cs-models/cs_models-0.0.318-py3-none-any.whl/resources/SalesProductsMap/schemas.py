from marshmallow import (
    Schema,
    fields,
    validate,
)


class SalesProductsMapResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    sales_table_id = fields.Integer(required=True)
    product_name = fields.String(required=True)
    source = fields.String(required=True)
    updated_at = fields.DateTime()
