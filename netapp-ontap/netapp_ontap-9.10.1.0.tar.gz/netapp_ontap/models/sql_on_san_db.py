r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SqlOnSanDb", "SqlOnSanDbSchema"]
__pdoc__ = {
    "SqlOnSanDbSchema.resource": False,
    "SqlOnSanDb": False,
}


class SqlOnSanDbSchema(ResourceSchema):
    """The fields of the SqlOnSanDb object"""

    size = Size(data_key="size")
    r""" The size of the DB. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    storage_service = fields.Nested("netapp_ontap.models.sql_on_san_db_storage_service.SqlOnSanDbStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the sql_on_san_db. """

    @property
    def resource(self):
        return SqlOnSanDb

    gettable_fields = [
        "size",
        "storage_service",
    ]
    """size,storage_service,"""

    patchable_fields = [
        "size",
        "storage_service",
    ]
    """size,storage_service,"""

    postable_fields = [
        "size",
        "storage_service",
    ]
    """size,storage_service,"""


class SqlOnSanDb(Resource):

    _schema = SqlOnSanDbSchema
