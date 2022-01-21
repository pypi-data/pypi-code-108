r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwareUpdateDetailsReferenceNode", "SoftwareUpdateDetailsReferenceNodeSchema"]
__pdoc__ = {
    "SoftwareUpdateDetailsReferenceNodeSchema.resource": False,
    "SoftwareUpdateDetailsReferenceNode": False,
}


class SoftwareUpdateDetailsReferenceNodeSchema(ResourceSchema):
    """The fields of the SoftwareUpdateDetailsReferenceNode object"""

    name = fields.Str(data_key="name")
    r""" Name of the node to be retrieved for update details.

Example: node1 """

    @property
    def resource(self):
        return SoftwareUpdateDetailsReferenceNode

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


class SoftwareUpdateDetailsReferenceNode(Resource):

    _schema = SoftwareUpdateDetailsReferenceNodeSchema
