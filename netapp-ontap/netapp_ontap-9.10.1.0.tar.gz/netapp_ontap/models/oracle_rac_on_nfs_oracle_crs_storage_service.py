r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["OracleRacOnNfsOracleCrsStorageService", "OracleRacOnNfsOracleCrsStorageServiceSchema"]
__pdoc__ = {
    "OracleRacOnNfsOracleCrsStorageServiceSchema.resource": False,
    "OracleRacOnNfsOracleCrsStorageService": False,
}


class OracleRacOnNfsOracleCrsStorageServiceSchema(ResourceSchema):
    """The fields of the OracleRacOnNfsOracleCrsStorageService object"""

    name = fields.Str(data_key="name")
    r""" The storage service of the Oracle CRS volume.

Valid choices:

* extreme
* performance
* value """

    @property
    def resource(self):
        return OracleRacOnNfsOracleCrsStorageService

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class OracleRacOnNfsOracleCrsStorageService(Resource):

    _schema = OracleRacOnNfsOracleCrsStorageServiceSchema
