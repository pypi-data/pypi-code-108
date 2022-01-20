from marshmallow import (
    Schema,
    fields,
    validate,
)


class UserSearchHistoryItemResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    user_id = fields.String(required=True, validate=not_blank)
    search_term = fields.String(required=True, validate=not_blank)
    search_type = fields.String(required=True)
    updated_at = fields.DateTime()


class UserSearchHistoryItemQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    user_id = fields.String(validate=not_blank)
    search_term = fields.String(validate=not_blank)
    search_type = fields.String(validate=not_blank)
