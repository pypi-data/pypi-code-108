from marshmallow import (
    Schema,
    fields,
    validate,
)


class CompanyReviewResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    company_sec_id = fields.Integer(allow_none=True)
    company_ous_id = fields.Integer(allow_none=True)
    note_tag = fields.String(allow_none=True)
    news_id = fields.Integer(allow_none=False)
    reviewed = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)
