r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["OracleOnNfsArchiveLog", "OracleOnNfsArchiveLogSchema"]
__pdoc__ = {
    "OracleOnNfsArchiveLogSchema.resource": False,
    "OracleOnNfsArchiveLog": False,
}


class OracleOnNfsArchiveLogSchema(ResourceSchema):
    """The fields of the OracleOnNfsArchiveLog object"""

    size = Size(data_key="size")
    r""" The size of the archive log. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    storage_service = fields.Nested("netapp_ontap.models.oracle_on_nfs_archive_log_storage_service.OracleOnNfsArchiveLogStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the oracle_on_nfs_archive_log. """

    @property
    def resource(self):
        return OracleOnNfsArchiveLog

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


class OracleOnNfsArchiveLog(Resource):

    _schema = OracleOnNfsArchiveLogSchema
