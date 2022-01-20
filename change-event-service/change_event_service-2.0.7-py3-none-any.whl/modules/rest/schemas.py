from marshmallow import Schema, fields, validate


class BaseResponseSchema(Schema):
    data = fields.Dict()
    message = fields.String()
    statusCode = fields.String()
    exceptionDetail = fields.String()

    class Meta:
        ordered = True


class ChangeEventSchema(Schema):
    id = fields.Integer(dump_only=True)
    ip = fields.String()
    user_id = fields.String()
    new_value = fields.String()
    object_id = fields.String()
    old_value = fields.String()
    user_name = fields.String()
    event_time = fields.DateTime()
    event_type = fields.String()
    field_name = fields.String()
    object_name = fields.String()
    tag = fields.List(fields.String(), validate=validate.Length(min=1))


class PaginationSchema(Schema):
    page = fields.Integer()
    total_pages = fields.Integer()
    total = fields.Integer()


class ChangeEventResponseSchema(BaseResponseSchema):
    data = fields.Nested(ChangeEventSchema)


class ChangeEventListResponseSchema(BaseResponseSchema):
    data = fields.Nested(ChangeEventSchema, many=True)
    page = fields.Nested(PaginationSchema)


class ChangeEventFilterRequestSchema(ChangeEventSchema):
    event_time = fields.List(fields.DateTime(), validate=validate.Length(min=2, max=2))


class ChangeEventFilterByTagRequestSchema(Schema):
    tags = fields.List(fields.String(), required=True, validate=validate.Length(min=1))
