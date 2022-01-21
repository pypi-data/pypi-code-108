r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ChassisNodeUsbsPorts", "ChassisNodeUsbsPortsSchema"]
__pdoc__ = {
    "ChassisNodeUsbsPortsSchema.resource": False,
    "ChassisNodeUsbsPorts": False,
}


class ChassisNodeUsbsPortsSchema(ResourceSchema):
    """The fields of the ChassisNodeUsbsPorts object"""

    connected = fields.Boolean(data_key="connected")
    r""" Indicates whether or not the USB port has a device connected to it. """

    @property
    def resource(self):
        return ChassisNodeUsbsPorts

    gettable_fields = [
        "connected",
    ]
    """connected,"""

    patchable_fields = [
        "connected",
    ]
    """connected,"""

    postable_fields = [
        "connected",
    ]
    """connected,"""


class ChassisNodeUsbsPorts(Resource):

    _schema = ChassisNodeUsbsPortsSchema
