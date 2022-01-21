r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["OracleOnNfsRedoLogStorageService", "OracleOnNfsRedoLogStorageServiceSchema"]
__pdoc__ = {
    "OracleOnNfsRedoLogStorageServiceSchema.resource": False,
    "OracleOnNfsRedoLogStorageService": False,
}


class OracleOnNfsRedoLogStorageServiceSchema(ResourceSchema):
    """The fields of the OracleOnNfsRedoLogStorageService object"""

    name = fields.Str(data_key="name")
    r""" The storage service of the redo log group.

Valid choices:

* extreme
* performance
* value """

    @property
    def resource(self):
        return OracleOnNfsRedoLogStorageService

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


class OracleOnNfsRedoLogStorageService(Resource):

    _schema = OracleOnNfsRedoLogStorageServiceSchema
