r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["TapeDeviceStoragePort", "TapeDeviceStoragePortSchema"]
__pdoc__ = {
    "TapeDeviceStoragePortSchema.resource": False,
    "TapeDeviceStoragePort": False,
}


class TapeDeviceStoragePortSchema(ResourceSchema):
    """The fields of the TapeDeviceStoragePort object"""

    name = fields.Str(data_key="name")
    r""" Initiator port.

Example: 2b """

    @property
    def resource(self):
        return TapeDeviceStoragePort

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


class TapeDeviceStoragePort(Resource):

    _schema = TapeDeviceStoragePortSchema
