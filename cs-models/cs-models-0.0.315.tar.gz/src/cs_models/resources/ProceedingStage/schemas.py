from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)
from ...utils.utils import pre_load_date_fields


class ProceedingStageResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    ptab2_proceeding_id = fields.Integer(required=True)
    stage = fields.String(required=True, validate=not_blank)
    is_active = fields.Boolean(required=True)
    filed_date = fields.DateTime(allow_none=True)
    due_date = fields.DateTime(allow_none=True)
    file_id = fields.Integer(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def convert_string_to_datetime(self, in_data):
        date_fields = [
            'filed_date',
            'due_date',
        ]

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%m-%d-%Y',
        )
        return in_data
