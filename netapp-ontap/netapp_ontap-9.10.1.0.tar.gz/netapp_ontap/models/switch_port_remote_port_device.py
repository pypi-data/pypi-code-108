r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SwitchPortRemotePortDevice", "SwitchPortRemotePortDeviceSchema"]
__pdoc__ = {
    "SwitchPortRemotePortDeviceSchema.resource": False,
    "SwitchPortRemotePortDevice": False,
}


class SwitchPortRemotePortDeviceSchema(ResourceSchema):
    """The fields of the SwitchPortRemotePortDevice object"""

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the switch_port_remote_port_device. """

    shelf = fields.Nested("netapp_ontap.resources.shelf.ShelfSchema", unknown=EXCLUDE, data_key="shelf")
    r""" The shelf field of the switch_port_remote_port_device. """

    @property
    def resource(self):
        return SwitchPortRemotePortDevice

    gettable_fields = [
        "node.links",
        "node.name",
        "node.uuid",
        "shelf.links",
        "shelf.uid",
    ]
    """node.links,node.name,node.uuid,shelf.links,shelf.uid,"""

    patchable_fields = [
        "node.name",
        "node.uuid",
        "shelf.uid",
    ]
    """node.name,node.uuid,shelf.uid,"""

    postable_fields = [
        "node.name",
        "node.uuid",
        "shelf.uid",
    ]
    """node.name,node.uuid,shelf.uid,"""


class SwitchPortRemotePortDevice(Resource):

    _schema = SwitchPortRemotePortDeviceSchema
