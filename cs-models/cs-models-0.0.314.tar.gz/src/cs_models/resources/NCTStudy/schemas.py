from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)
from ...utils.utils import pre_load_date_fields


class NCTStudyResourceSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    id = fields.Integer(dump_only=True)
    nct_id = fields.String(allow_none=False, validate=not_blank)
    brief_title = fields.String(allow_none=True)
    study_status = fields.String(allow_none=True)
    study_type = fields.String(allow_none=True)
    study_start_date = fields.DateTime(allow_none=True)
    last_update_submitted_qc_date = fields.DateTime(allow_none=True)
    phase = fields.String(allow_none=True)
    sponsors = fields.String(allow_none=True)
    conditions = fields.String(allow_none=True)
    industry_flag = fields.Boolean()
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = ['study_start_date', 'last_update_submitted_qc_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%Y-%m-%d',
        )
        return in_data
