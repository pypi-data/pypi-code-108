from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    ValidationError,
)


class WatchlistResourceSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    id = fields.Integer(dump_only=True)
    user_id = fields.String(required=True, validate=not_blank)
    resource_type = fields.String(required=True)
    norm_cui = fields.String(allow_none=True)
    condition_id = fields.Integer(allow_none=True)
    company_sec_id = fields.Integer(allow_none=True)
    company_ous_id = fields.Integer(allow_none=True)
    ptab2_proceeding_id = fields.Integer(allow_none=True)
    is_active = fields.Boolean(required=True)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def check_resource_info(self, in_data):
        if self._get_number_of_resource_fields(in_data) == 0:
            raise ValidationError('Provide at least one resource info')

    def _get_number_of_resource_fields(self, in_data):
        result = 0
        if 'norm_cui' in in_data:
            if in_data['norm_cui'] is not None:
                result += 1
        if 'condition_id' in in_data:
            if in_data['condition_id'] is not None:
                result += 1
        if 'company_sec_id' in in_data:
            if in_data['company_sec_id'] is not None:
                result += 1
        if 'company_ous_id' in in_data:
            if in_data['company_ous_id'] is not None:
                result += 1
        if 'ptab2_proceeding_id' in in_data:
            if in_data['ptab2_proceeding_id'] is not None:
                result += 1
        return result
