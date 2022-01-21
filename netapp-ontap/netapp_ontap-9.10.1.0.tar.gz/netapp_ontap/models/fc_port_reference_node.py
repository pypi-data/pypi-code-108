r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FcPortReferenceNode", "FcPortReferenceNodeSchema"]
__pdoc__ = {
    "FcPortReferenceNodeSchema.resource": False,
    "FcPortReferenceNode": False,
}


class FcPortReferenceNodeSchema(ResourceSchema):
    """The fields of the FcPortReferenceNode object"""

    name = fields.Str(data_key="name")
    r""" The name of the node on which the FC port is located.


Example: node1 """

    @property
    def resource(self):
        return FcPortReferenceNode

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


class FcPortReferenceNode(Resource):

    _schema = FcPortReferenceNodeSchema
