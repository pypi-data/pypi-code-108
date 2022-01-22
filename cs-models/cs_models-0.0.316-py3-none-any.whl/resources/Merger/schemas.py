from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    ValidationError,
)
from ...utils.utils import pre_load_date_fields


class MergerResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    target_sec_id = fields.Integer(allow_none=True)
    target_ous_id = fields.Integer(allow_none=True)
    acquirer_sec_id = fields.Integer(allow_none=True)
    acquirer_ous_id = fields.Integer(allow_none=True)
    deal_value = fields.Decimal()
    type = fields.String()
    announcement_date = fields.DateTime(required=True)
    offer_price = fields.Float()
    market_price = fields.Float()
    dma_file_id = fields.Integer()
    updated_at = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['announcement_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%m/%d/%Y',
        )
        return in_data

    @pre_load
    def check_target_acquirer_ids(self, in_data):
        if self._get_number_of_target_company_fields(in_data) != 1:
            raise ValidationError('Provide either company_sec_id or '
                                  'company_ous_id for target, not both')
        if self._get_number_of_acquirer_company_fields(in_data) != 1:
            raise ValidationError('Provide either company_sec_id or '
                                  'company_ous_id for acquirer, not both')

    def _get_number_of_target_company_fields(self, in_data):
        result = 0
        if 'target_sec_id' in in_data:
            if in_data['target_sec_id'] is not None:
                result += 1
        if 'target_ous_id' in in_data:
            if in_data['target_ous_id'] is not None:
                result += 1
        return result

    def _get_number_of_acquirer_company_fields(self, in_data):
        result = 0
        if 'acquirer_sec_id' in in_data:
            if in_data['acquirer_sec_id'] is not None:
                result += 1
        if 'acquirer_ous_id' in in_data:
            if in_data['acquirer_ous_id'] is not None:
                result += 1
        return result


class MergerQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    target_sec_id = fields.Integer()
    target_ous_id = fields.Integer()
    acquirer_sec_id = fields.Integer()
    acquirer_ous_id = fields.Integer()
    deal_value = fields.Decimal()
    type = fields.String()
    announcement_date = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['announcement_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%m/%d/%Y',
        )
        return in_data


class MergerPatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    target_sec_id = fields.Integer()
    target_ous_id = fields.Integer()
    acquirer_sec_id = fields.Integer()
    acquirer_ous_id = fields.Integer()
    deal_value = fields.Decimal()
    type = fields.String()
    announcement_date = fields.DateTime(required=True)
    offer_price = fields.Float()
    market_price = fields.Float()
    dma_file_id = fields.Integer()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['announcement_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%m/%d/%Y',
        )
        return in_data

    @pre_load
    def check_target_acquirer_ids(self, in_data):
        if self._get_number_of_target_company_fields(in_data) != 1:
            raise ValidationError('Provide either company_sec_id or '
                                  'company_ous_id for target, not both')
        if self._get_number_of_acquirer_company_fields(in_data) != 1:
            raise ValidationError('Provide either company_sec_id or '
                                  'company_ous_id for acquirer, not both')

    def _get_number_of_target_company_fields(self, in_data):
        result = 0
        if 'target_sec_id' in in_data:
            if in_data['target_sec_id'] is not None:
                result += 1
        if 'target_ous_id' in in_data:
            if in_data['target_ous_id'] is not None:
                result += 1
        return result

    def _get_number_of_acquirer_company_fields(self, in_data):
        result = 0
        if 'acquirer_sec_id' in in_data:
            if in_data['acquirer_sec_id'] is not None:
                result += 1
        if 'acquirer_ous_id' in in_data:
            if in_data['acquirer_ous_id'] is not None:
                result += 1
        return result
