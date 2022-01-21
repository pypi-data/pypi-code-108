r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["OracleOnNfsRedoLog", "OracleOnNfsRedoLogSchema"]
__pdoc__ = {
    "OracleOnNfsRedoLogSchema.resource": False,
    "OracleOnNfsRedoLog": False,
}


class OracleOnNfsRedoLogSchema(ResourceSchema):
    """The fields of the OracleOnNfsRedoLog object"""

    mirrored = fields.Boolean(data_key="mirrored")
    r""" Specifies whether the redo log group should be mirrored. """

    size = Size(data_key="size")
    r""" The size of the redo log group. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    storage_service = fields.Nested("netapp_ontap.models.oracle_on_nfs_redo_log_storage_service.OracleOnNfsRedoLogStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the oracle_on_nfs_redo_log. """

    @property
    def resource(self):
        return OracleOnNfsRedoLog

    gettable_fields = [
        "mirrored",
        "size",
        "storage_service",
    ]
    """mirrored,size,storage_service,"""

    patchable_fields = [
        "size",
        "storage_service",
    ]
    """size,storage_service,"""

    postable_fields = [
        "mirrored",
        "size",
        "storage_service",
    ]
    """mirrored,size,storage_service,"""


class OracleOnNfsRedoLog(Resource):

    _schema = OracleOnNfsRedoLogSchema
