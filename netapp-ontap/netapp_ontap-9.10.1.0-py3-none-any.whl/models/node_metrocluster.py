r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeMetrocluster", "NodeMetroclusterSchema"]
__pdoc__ = {
    "NodeMetroclusterSchema.resource": False,
    "NodeMetrocluster": False,
}


class NodeMetroclusterSchema(ResourceSchema):
    """The fields of the NodeMetrocluster object"""

    custom_vlan_capable = fields.Boolean(data_key="custom_vlan_capable")
    r""" Indicates whether the MetroCluster over IP platform supports custom VLAN IDs. """

    ports = fields.List(fields.Nested("netapp_ontap.models.node_metrocluster_ports.NodeMetroclusterPortsSchema", unknown=EXCLUDE), data_key="ports")
    r""" MetroCluster over IP ports. """

    type = fields.Str(data_key="type")
    r""" The Metrocluster configuration type

Valid choices:

* fc
* fc_2_node
* ip """

    @property
    def resource(self):
        return NodeMetrocluster

    gettable_fields = [
        "custom_vlan_capable",
        "ports",
        "type",
    ]
    """custom_vlan_capable,ports,type,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NodeMetrocluster(Resource):

    _schema = NodeMetroclusterSchema
