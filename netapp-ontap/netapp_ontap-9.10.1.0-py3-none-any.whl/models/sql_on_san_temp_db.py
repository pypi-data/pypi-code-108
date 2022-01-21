r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SqlOnSanTempDb", "SqlOnSanTempDbSchema"]
__pdoc__ = {
    "SqlOnSanTempDbSchema.resource": False,
    "SqlOnSanTempDb": False,
}


class SqlOnSanTempDbSchema(ResourceSchema):
    """The fields of the SqlOnSanTempDb object"""

    size = Size(data_key="size")
    r""" The size of the temp DB. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    storage_service = fields.Nested("netapp_ontap.models.sql_on_san_temp_db_storage_service.SqlOnSanTempDbStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the sql_on_san_temp_db. """

    @property
    def resource(self):
        return SqlOnSanTempDb

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


class SqlOnSanTempDb(Resource):

    _schema = SqlOnSanTempDbSchema
