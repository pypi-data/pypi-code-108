r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ChassisNodeUsbs", "ChassisNodeUsbsSchema"]
__pdoc__ = {
    "ChassisNodeUsbsSchema.resource": False,
    "ChassisNodeUsbs": False,
}


class ChassisNodeUsbsSchema(ResourceSchema):
    """The fields of the ChassisNodeUsbs object"""

    enabled = fields.Boolean(data_key="enabled")
    r""" Indicates whether or not the USB ports are enabled. """

    ports = fields.List(fields.Nested("netapp_ontap.models.chassis_node_usbs_ports.ChassisNodeUsbsPortsSchema", unknown=EXCLUDE), data_key="ports")
    r""" The ports field of the chassis_node_usbs. """

    supported = fields.Boolean(data_key="supported")
    r""" Indicates whether or not USB ports are supported on the current platform. """

    @property
    def resource(self):
        return ChassisNodeUsbs

    gettable_fields = [
        "enabled",
        "ports",
        "supported",
    ]
    """enabled,ports,supported,"""

    patchable_fields = [
        "enabled",
        "ports",
        "supported",
    ]
    """enabled,ports,supported,"""

    postable_fields = [
        "enabled",
        "ports",
        "supported",
    ]
    """enabled,ports,supported,"""


class ChassisNodeUsbs(Resource):

    _schema = ChassisNodeUsbsSchema
