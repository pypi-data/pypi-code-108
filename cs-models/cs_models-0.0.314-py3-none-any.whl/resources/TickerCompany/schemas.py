from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    ValidationError,
)


class TickerCompanyResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    ticker = fields.String(required=True, validate=not_blank)
    exchange = fields.String(allow_none=True)
    company_sec_id = fields.Integer(allow_none=True)
    company_ous_id = fields.Integer(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def pre_load(self, in_data):
        if self._get_number_of_company_fields(in_data) > 1:
            raise ValidationError('Provide either company_sec_id or '
                                  'company_ous_id, not both')

    def _get_number_of_company_fields(self, in_data):
        result = 0
        if 'company_sec_id' in in_data:
            if in_data['company_sec_id'] is not None:
                result += 1
        if 'company_ous_id' in in_data:
            if in_data['company_ous_id'] is not None:
                result += 1
        return result
