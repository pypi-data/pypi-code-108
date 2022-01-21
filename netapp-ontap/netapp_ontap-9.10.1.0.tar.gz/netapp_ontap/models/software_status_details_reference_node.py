r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwareStatusDetailsReferenceNode", "SoftwareStatusDetailsReferenceNodeSchema"]
__pdoc__ = {
    "SoftwareStatusDetailsReferenceNodeSchema.resource": False,
    "SoftwareStatusDetailsReferenceNode": False,
}


class SoftwareStatusDetailsReferenceNodeSchema(ResourceSchema):
    """The fields of the SoftwareStatusDetailsReferenceNode object"""

    name = fields.Str(data_key="name")
    r""" Name of the node to be retrieved for status details.

Example: node1 """

    @property
    def resource(self):
        return SoftwareStatusDetailsReferenceNode

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class SoftwareStatusDetailsReferenceNode(Resource):

    _schema = SoftwareStatusDetailsReferenceNodeSchema
