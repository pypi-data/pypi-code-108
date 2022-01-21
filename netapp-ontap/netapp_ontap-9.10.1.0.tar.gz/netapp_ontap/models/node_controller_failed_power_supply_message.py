r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeControllerFailedPowerSupplyMessage", "NodeControllerFailedPowerSupplyMessageSchema"]
__pdoc__ = {
    "NodeControllerFailedPowerSupplyMessageSchema.resource": False,
    "NodeControllerFailedPowerSupplyMessage": False,
}


class NodeControllerFailedPowerSupplyMessageSchema(ResourceSchema):
    """The fields of the NodeControllerFailedPowerSupplyMessage object"""

    code = fields.Str(data_key="code")
    r""" Error code describing the current condition of power supply.

Example: 111411208 """

    message = fields.Str(data_key="message")
    r""" Message describing the state of any power supplies that are currently degraded. It is only of use when `failed_power_supply.count` is not zero.

Example: There are no failed power supplies. """

    @property
    def resource(self):
        return NodeControllerFailedPowerSupplyMessage

    gettable_fields = [
        "code",
        "message",
    ]
    """code,message,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NodeControllerFailedPowerSupplyMessage(Resource):

    _schema = NodeControllerFailedPowerSupplyMessageSchema
