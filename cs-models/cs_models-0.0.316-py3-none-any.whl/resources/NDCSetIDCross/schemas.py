from marshmallow import (
    Schema,
    fields,
)


class NDCSetIDCrossResourceSchema(Schema):
    product_ndc = fields.String(allow_none=True)
    package_ndc = fields.String(allow_none=True)
    spl_set_id = fields.String(allow_none=True)


class NDCSetIDCrossQueryParamsSchema(Schema):
    product_ndc = fields.String(allow_none=True)
    package_ndc = fields.String(allow_none=True)
    spl_set_id = fields.String(allow_none=True)


class NDCSetIDCrossPatchSchema(Schema):
    product_ndc = fields.String(allow_none=True)
    package_ndc = fields.String(allow_none=True)
    spl_set_id = fields.String(allow_none=True)

