r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeMetroclusterPorts", "NodeMetroclusterPortsSchema"]
__pdoc__ = {
    "NodeMetroclusterPortsSchema.resource": False,
    "NodeMetroclusterPorts": False,
}


class NodeMetroclusterPortsSchema(ResourceSchema):
    """The fields of the NodeMetroclusterPorts object"""

    name = fields.Str(data_key="name")
    r""" The name field of the node_metrocluster_ports.

Example: e1b """

    @property
    def resource(self):
        return NodeMetroclusterPorts

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


class NodeMetroclusterPorts(Resource):

    _schema = NodeMetroclusterPortsSchema
