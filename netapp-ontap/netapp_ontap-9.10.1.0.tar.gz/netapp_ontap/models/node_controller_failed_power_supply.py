r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeControllerFailedPowerSupply", "NodeControllerFailedPowerSupplySchema"]
__pdoc__ = {
    "NodeControllerFailedPowerSupplySchema.resource": False,
    "NodeControllerFailedPowerSupply": False,
}


class NodeControllerFailedPowerSupplySchema(ResourceSchema):
    """The fields of the NodeControllerFailedPowerSupply object"""

    count = Size(data_key="count")
    r""" Number of failed power supply units.

Example: 1 """

    message = fields.Nested("netapp_ontap.models.node_controller_failed_power_supply_message.NodeControllerFailedPowerSupplyMessageSchema", unknown=EXCLUDE, data_key="message")
    r""" The message field of the node_controller_failed_power_supply. """

    @property
    def resource(self):
        return NodeControllerFailedPowerSupply

    gettable_fields = [
        "count",
        "message",
    ]
    """count,message,"""

    patchable_fields = [
        "message",
    ]
    """message,"""

    postable_fields = [
        "message",
    ]
    """message,"""


class NodeControllerFailedPowerSupply(Resource):

    _schema = NodeControllerFailedPowerSupplySchema
