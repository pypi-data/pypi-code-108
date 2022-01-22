from marshmallow import (
    Schema,
    fields,
    validate,
)


class NDCResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    spl_id = fields.String(validate=not_blank, required=True)
    product_ndc = fields.String(validate=not_blank, required=True)
    package_ndc = fields.String(validate=not_blank, required=True)
    spl_set_id = fields.String(allow_none=True)
    appl_no = fields.String(allow_none=True)
    appl_type = fields.String(allow_none=True)
    route = fields.String(allow_none=True)
    dosage_form = fields.String(allow_none=True)
    generic_name = fields.String(allow_none=True)
    labeler_name = fields.String(allow_none=True)
    brand_name = fields.String(allow_none=True)
    marketing_category = fields.String(allow_none=True)
    marketing_start_date = fields.DateTime(allow_none=True)
    marketing_end_date = fields.DateTime(allow_none=True)
    labeler_subsidiary_id = fields.Integer(allow_none=True)
    updated_at = fields.DateTime()


class NDCQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    spl_id = fields.String(validate=not_blank)
    product_ndc = fields.String(validate=not_blank)
    package_ndc = fields.String(validate=not_blank)
    route = fields.String(validate=not_blank)


class NDCPatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    spl_id = fields.String(validate=not_blank)
    product_ndc = fields.String(validate=not_blank)
    package_ndc = fields.String(validate=not_blank)
    spl_set_id = fields.String(allow_none=True)
    appl_no = fields.String(allow_none=True)
    appl_type = fields.String(allow_none=True)
    route = fields.String(allow_none=True)
    dosage_form = fields.String(allow_none=True)
    generic_name = fields.String(allow_none=True)
    labeler_name = fields.String(allow_none=True)
    brand_name = fields.String(allow_none=True)
    marketing_category = fields.String(allow_none=True)
    marketing_start_date = fields.DateTime(allow_none=True)
    marketing_end_date = fields.DateTime(allow_none=True)
    labeler_subsidiary_id = fields.Integer(allow_none=True)
