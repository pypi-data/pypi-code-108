r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["PortReferenceNode", "PortReferenceNodeSchema"]
__pdoc__ = {
    "PortReferenceNodeSchema.resource": False,
    "PortReferenceNode": False,
}


class PortReferenceNodeSchema(ResourceSchema):
    """The fields of the PortReferenceNode object"""

    name = fields.Str(data_key="name")
    r""" Name of node on which the port is located.

Example: node1 """

    @property
    def resource(self):
        return PortReferenceNode

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


class PortReferenceNode(Resource):

    _schema = PortReferenceNodeSchema
