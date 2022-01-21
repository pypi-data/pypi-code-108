r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["OracleRacOnNfsGridBinaryStorageService", "OracleRacOnNfsGridBinaryStorageServiceSchema"]
__pdoc__ = {
    "OracleRacOnNfsGridBinaryStorageServiceSchema.resource": False,
    "OracleRacOnNfsGridBinaryStorageService": False,
}


class OracleRacOnNfsGridBinaryStorageServiceSchema(ResourceSchema):
    """The fields of the OracleRacOnNfsGridBinaryStorageService object"""

    name = fields.Str(data_key="name")
    r""" The storage service of the Oracle grid binary storage volume.

Valid choices:

* extreme
* performance
* value """

    @property
    def resource(self):
        return OracleRacOnNfsGridBinaryStorageService

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


class OracleRacOnNfsGridBinaryStorageService(Resource):

    _schema = OracleRacOnNfsGridBinaryStorageServiceSchema
