from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)
from ...utils.utils import pre_load_date_fields


class LatestPipelineProductResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    product_name = fields.String(validate=not_blank, required=True)
    intervention_id = fields.Integer(required=True)
    news_id = fields.Integer()
    latest_catalyst_date = fields.DateTime()
    updated_at = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['latest_catalyst_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%Y%m%dT%H%M%S',
        )
        return in_data


class LatestPipelinePatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    product_name = fields.String(validate=not_blank, required=True)
    intervention_id = fields.Integer(required=True)
    news_id = fields.Integer()
    latest_catalyst_date = fields.DateTime()
    updated_at = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['latest_catalyst_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%Y%m%dT%H%M%S',
        )
        return in_data
