r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ChassisNode", "ChassisNodeSchema"]
__pdoc__ = {
    "ChassisNodeSchema.resource": False,
    "ChassisNode": False,
}


class ChassisNodeSchema(ResourceSchema):
    """The fields of the ChassisNode object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the chassis_node. """

    name = fields.Str(data_key="name")
    r""" The name field of the chassis_node.

Example: node1 """

    pcis = fields.Nested("netapp_ontap.models.chassis_node_pcis.ChassisNodePcisSchema", unknown=EXCLUDE, data_key="pcis")
    r""" The pcis field of the chassis_node. """

    position = fields.Str(data_key="position")
    r""" The Position of the Node in the Chassis

Valid choices:

* top
* bottom
* left
* right
* unknown """

    usbs = fields.Nested("netapp_ontap.models.chassis_node_usbs.ChassisNodeUsbsSchema", unknown=EXCLUDE, data_key="usbs")
    r""" The usbs field of the chassis_node. """

    uuid = fields.Str(data_key="uuid")
    r""" The uuid field of the chassis_node.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return ChassisNode

    gettable_fields = [
        "links",
        "name",
        "pcis",
        "position",
        "usbs",
        "uuid",
    ]
    """links,name,pcis,position,usbs,uuid,"""

    patchable_fields = [
        "name",
        "pcis",
        "position",
        "usbs",
        "uuid",
    ]
    """name,pcis,position,usbs,uuid,"""

    postable_fields = [
        "name",
        "pcis",
        "position",
        "usbs",
        "uuid",
    ]
    """name,pcis,position,usbs,uuid,"""


class ChassisNode(Resource):

    _schema = ChassisNodeSchema
