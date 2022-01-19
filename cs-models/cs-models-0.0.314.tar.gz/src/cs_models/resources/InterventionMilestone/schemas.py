from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)
from ...utils.utils import pre_load_date_fields


class InterventionMilestoneResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_condition_id = fields.Integer(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
    milestone = fields.String(validate=not_blank, required=True)
    description = fields.String(allow_none=True)
    source_url = fields.String(allow_none=True)
    news_id = fields.Integer(allow_none=True)
    sec_filing_id = fields.Integer(allow_none=True)
    is_deleted = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['start_date', 'end_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format="%Y%m%dT%H%M%S",
        )
        return in_data


class InterventionMilestonePatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')
    id = fields.Integer(required=True)
    is_deleted = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime()
