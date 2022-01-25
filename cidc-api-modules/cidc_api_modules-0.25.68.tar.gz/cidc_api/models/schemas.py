__all__ = [
    "BaseSchema",
    "DownloadableFileSchema",
    "DownloadableFileListSchema",
    "PermissionSchema",
    "PermissionListSchema",
    "TrialMetadataSchema",
    "TrialMetadataListSchema",
    "UploadJobSchema",
    "UploadJobListSchema",
    "UserSchema",
    "UserListSchema",
]

from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from ..config.db import db
from .models import (
    UploadJobs,
    Users,
    DownloadableFiles,
    Permissions,
    TrialMetadata,
)


class BaseSchema(SQLAlchemyAutoSchema):
    class Meta:
        sqla_session = db.session
        include_fk = True
        load_instance = True

    # Read-only fields common across all schemas
    _created = fields.DateTime(dump_only=True)
    _updated = fields.DateTime(dump_only=True)
    _etag = fields.Str(dump_only=True)


class _ListMetadata(BaseSchema):
    total = fields.Int(required=True)
    # TODO: do we need these fields?
    # page_num = fields.Int(required=True)
    # page_size = fields.Int(required=True)


def _make_list_schema(schema: BaseSchema):
    class ListSchema(BaseSchema):
        _items = fields.List(fields.Nested(schema), required=True)
        _meta = fields.Nested(_ListMetadata(), required=True)

    return ListSchema


class UploadJobSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = UploadJobs
        exclude = ["_status"]

    status = auto_field(column_name="_status")


UploadJobListSchema = _make_list_schema(UploadJobSchema())


class UserSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Users

    _accessed = fields.DateTime(dump_only=True)


UserListSchema = _make_list_schema(UserSchema())


class DownloadableFileSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = DownloadableFiles

    file_ext = fields.Str(dump_only=True)
    data_category = fields.Str(dump_only=True)
    data_category_prefix = fields.Str(dump_only=True)
    cimac_id = fields.Str(dump_only=True)
    file_purpose = fields.Str(dump_only=True)
    short_description = fields.Str(dump_only=True)
    long_description = fields.Str(dump_only=True)


DownloadableFileListSchema = _make_list_schema(DownloadableFileSchema())


class PermissionSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Permissions


PermissionListSchema = _make_list_schema(PermissionSchema())


class TrialMetadataSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = TrialMetadata

    file_bundle = fields.Dict(dump_only=True)
    num_participants = fields.Int(dump_only=True)
    num_samples = fields.Int(dump_only=True)


TrialMetadataListSchema = _make_list_schema(TrialMetadataSchema())
