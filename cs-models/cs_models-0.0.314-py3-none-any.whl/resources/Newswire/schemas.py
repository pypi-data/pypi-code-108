from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)
from ...utils.utils import pre_load_date_fields


class NewswireResourceSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    id = fields.Integer(dump_only=True)
    date = fields.DateTime(required=True)
    tzinfo = fields.String(allow_none=True)
    source = fields.String(required=True)
    headline = fields.String(required=True)
    drugs = fields.String(allow_none=True)
    conditions = fields.String(allow_none=True)
    filtered_drugs = fields.String(allow_none=True)
    filtered_conditions = fields.String(allow_none=True)
    news_file_id = fields.Integer(required=True)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%Y%m%dT%H%M%S',
        )
        return in_data


class NewswireQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    id = fields.Integer()
    date = fields.DateTime()
    tzinfo = fields.String()
    source = fields.String()
    headline = fields.String()
    drugs = fields.String()
    conditions = fields.String()
    filtered_drugs = fields.String()
    filtered_conditions = fields.String()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%Y%m%dT%H%M%S',
        )
        return in_data


class NewswirePatchSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    date = fields.DateTime(allow_none=False)
    tzinfo = fields.String()
    source = fields.String(allow_none=False)
    headline = fields.String(allow_none=False)
    drugs = fields.String(allow_none=True)
    conditions = fields.String(allow_none=True)
    filtered_drugs = fields.String(allow_none=True)
    filtered_conditions = fields.String(allow_none=True)
    news_file_id = fields.Integer(allow_none=True)

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%Y%m%dT%H%M%S',
        )
        return in_data