r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["OracleOnNfsDb", "OracleOnNfsDbSchema"]
__pdoc__ = {
    "OracleOnNfsDbSchema.resource": False,
    "OracleOnNfsDb": False,
}


class OracleOnNfsDbSchema(ResourceSchema):
    """The fields of the OracleOnNfsDb object"""

    size = Size(data_key="size")
    r""" The size of the database. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    storage_service = fields.Nested("netapp_ontap.models.mongo_db_on_san_dataset_storage_service.MongoDbOnSanDatasetStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the oracle_on_nfs_db. """

    @property
    def resource(self):
        return OracleOnNfsDb

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


class OracleOnNfsDb(Resource):

    _schema = OracleOnNfsDbSchema
