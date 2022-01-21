r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["OracleRacOnNfsOracleCrs", "OracleRacOnNfsOracleCrsSchema"]
__pdoc__ = {
    "OracleRacOnNfsOracleCrsSchema.resource": False,
    "OracleRacOnNfsOracleCrs": False,
}


class OracleRacOnNfsOracleCrsSchema(ResourceSchema):
    """The fields of the OracleRacOnNfsOracleCrs object"""

    copies = Size(data_key="copies")
    r""" The number of CRS volumes. """

    size = Size(data_key="size")
    r""" The size of the Oracle CRS/voting storage volume. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    storage_service = fields.Nested("netapp_ontap.models.oracle_rac_on_nfs_oracle_crs_storage_service.OracleRacOnNfsOracleCrsStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the oracle_rac_on_nfs_oracle_crs. """

    @property
    def resource(self):
        return OracleRacOnNfsOracleCrs

    gettable_fields = [
        "copies",
        "size",
        "storage_service",
    ]
    """copies,size,storage_service,"""

    patchable_fields = [
        "storage_service",
    ]
    """storage_service,"""

    postable_fields = [
        "copies",
        "size",
        "storage_service",
    ]
    """copies,size,storage_service,"""


class OracleRacOnNfsOracleCrs(Resource):

    _schema = OracleRacOnNfsOracleCrsSchema
