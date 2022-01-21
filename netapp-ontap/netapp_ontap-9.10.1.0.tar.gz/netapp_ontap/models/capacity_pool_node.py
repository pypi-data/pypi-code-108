r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["CapacityPoolNode", "CapacityPoolNodeSchema"]
__pdoc__ = {
    "CapacityPoolNodeSchema.resource": False,
    "CapacityPoolNode": False,
}


class CapacityPoolNodeSchema(ResourceSchema):
    """The fields of the CapacityPoolNode object"""

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the capacity_pool_node. """

    used_size = Size(data_key="used_size")
    r""" Capacity, in bytes, that is currently used by the node. """

    @property
    def resource(self):
        return CapacityPoolNode

    gettable_fields = [
        "node.links",
        "node.name",
        "node.uuid",
        "used_size",
    ]
    """node.links,node.name,node.uuid,used_size,"""

    patchable_fields = [
        "node.name",
        "node.uuid",
    ]
    """node.name,node.uuid,"""

    postable_fields = [
        "node.name",
        "node.uuid",
    ]
    """node.name,node.uuid,"""


class CapacityPoolNode(Resource):

    _schema = CapacityPoolNodeSchema
