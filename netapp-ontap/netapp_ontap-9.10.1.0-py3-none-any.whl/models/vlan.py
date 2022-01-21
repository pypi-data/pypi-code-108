r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Vlan", "VlanSchema"]
__pdoc__ = {
    "VlanSchema.resource": False,
    "Vlan": False,
}


class VlanSchema(ResourceSchema):
    """The fields of the Vlan object"""

    port = fields.Nested("netapp_ontap.models.node_metrocluster_ports.NodeMetroclusterPortsSchema", unknown=EXCLUDE, data_key="port")
    r""" The port field of the vlan. """

    tag = Size(data_key="tag")
    r""" VLAN ID

Example: 200 """

    @property
    def resource(self):
        return Vlan

    gettable_fields = [
        "port",
        "tag",
    ]
    """port,tag,"""

    patchable_fields = [
        "port",
        "tag",
    ]
    """port,tag,"""

    postable_fields = [
        "port",
        "tag",
    ]
    """port,tag,"""


class Vlan(Resource):

    _schema = VlanSchema
