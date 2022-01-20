from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)

from ...utils.utils import pre_load_date_fields


class OrangeBookExclusivityResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    appl_no = fields.String(required=True, validate=not_blank)
    appl_type = fields.String(required=True, validate=not_blank)
    product_no = fields.String(required=True, validate=not_blank)
    exclusivity_code = fields.String(required=True, validate=not_blank)
    exclusivity_date = fields.DateTime(allow_none=True)

    @pre_load
    def load_date_fields(self, in_data):
        date_fields = ['exclusivity_date']
        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%b %d, %Y',
        )
        return in_data


class OrangeBookExclusivityQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    appl_type = fields.String(validate=not_blank)
    appl_no = fields.String(validate=not_blank)
    product_no = fields.String(validate=not_blank)
    exclusivity_code = fields.String(validate=not_blank)
