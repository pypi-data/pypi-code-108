r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["DrNode", "DrNodeSchema"]
__pdoc__ = {
    "DrNodeSchema.resource": False,
    "DrNode": False,
}


class DrNodeSchema(ResourceSchema):
    """The fields of the DrNode object"""

    name = fields.Str(data_key="name")
    r""" The name field of the dr_node.

Example: node1 """

    uuid = fields.Str(data_key="uuid")
    r""" The uuid field of the dr_node.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return DrNode

    gettable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class DrNode(Resource):

    _schema = DrNodeSchema
