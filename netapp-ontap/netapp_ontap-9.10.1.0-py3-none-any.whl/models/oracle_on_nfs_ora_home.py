r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["OracleOnNfsOraHome", "OracleOnNfsOraHomeSchema"]
__pdoc__ = {
    "OracleOnNfsOraHomeSchema.resource": False,
    "OracleOnNfsOraHome": False,
}


class OracleOnNfsOraHomeSchema(ResourceSchema):
    """The fields of the OracleOnNfsOraHome object"""

    size = Size(data_key="size")
    r""" The size of the ORACLE_HOME storage volume. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    storage_service = fields.Nested("netapp_ontap.models.oracle_on_nfs_ora_home_storage_service.OracleOnNfsOraHomeStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the oracle_on_nfs_ora_home. """

    @property
    def resource(self):
        return OracleOnNfsOraHome

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


class OracleOnNfsOraHome(Resource):

    _schema = OracleOnNfsOraHomeSchema
