from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)

from ...utils.utils import pre_load_date_fields


class RegulatoryApprovalOutboxResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    date = fields.DateTime(required=True)
    news_id = fields.Integer(required=True)
    approval_text = fields.String(validate=not_blank)
    intervention_id = fields.Integer(allow_none=True)
    condition_id = fields.Integer(allow_none=True)
    geography = fields.String(allow_none=True)
    stage = fields.Integer(allow_none=True)
    updated_at = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format="%Y%m%dT%H%M%S",
        )
        return in_data
