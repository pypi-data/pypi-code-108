from marshmallow import (
    Schema,
    fields,
    validate,
)


class CompanySECResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    cik_str = fields.String(required=True, validate=not_blank)
    ticker = fields.String(allow_none=True)
    title = fields.String(required=True)
    exchange = fields.String(allow_none=True)
    company_url = fields.String(allow_none=True)
    pipeline_url = fields.String(allow_none=True)
    ir_url = fields.String(allow_none=True)
    is_activated = fields.Boolean(allow_none=True)
    is_biopharma = fields.Boolean(allow_none=True)
    discarded = fields.Boolean(allow_none=True)
    skip_sec = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)


class CompanySECUpdateSchema(Schema):
    id = fields.Integer()
    company_url = fields.String(allow_none=True)
    pipeline_url = fields.String(allow_none=True)
    ir_url = fields.String(allow_none=True)
    is_activated = fields.Boolean(allow_none=True)
    is_biopharma = fields.Boolean(allow_none=True)
    discarded = fields.Boolean(allow_none=True)
    skip_sec = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)
