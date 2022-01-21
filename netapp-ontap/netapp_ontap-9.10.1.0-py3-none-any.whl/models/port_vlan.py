r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["PortVlan", "PortVlanSchema"]
__pdoc__ = {
    "PortVlanSchema.resource": False,
    "PortVlan": False,
}


class PortVlanSchema(ResourceSchema):
    """The fields of the PortVlan object"""

    base_port = fields.Nested("netapp_ontap.resources.port.PortSchema", unknown=EXCLUDE, data_key="base_port")
    r""" The base_port field of the port_vlan. """

    tag = Size(data_key="tag")
    r""" VLAN ID

Example: 100 """

    @property
    def resource(self):
        return PortVlan

    gettable_fields = [
        "base_port.links",
        "base_port.name",
        "base_port.node",
        "base_port.uuid",
        "tag",
    ]
    """base_port.links,base_port.name,base_port.node,base_port.uuid,tag,"""

    patchable_fields = [
        "base_port.name",
        "base_port.node",
        "base_port.uuid",
        "tag",
    ]
    """base_port.name,base_port.node,base_port.uuid,tag,"""

    postable_fields = [
        "base_port.name",
        "base_port.node",
        "base_port.uuid",
        "tag",
    ]
    """base_port.name,base_port.node,base_port.uuid,tag,"""


class PortVlan(Resource):

    _schema = PortVlanSchema
