r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeControllerFailedFanMessage", "NodeControllerFailedFanMessageSchema"]
__pdoc__ = {
    "NodeControllerFailedFanMessageSchema.resource": False,
    "NodeControllerFailedFanMessage": False,
}


class NodeControllerFailedFanMessageSchema(ResourceSchema):
    """The fields of the NodeControllerFailedFanMessage object"""

    code = fields.Str(data_key="code")
    r""" Error code describing the current condition of chassis fans.

Example: 111411207 """

    message = fields.Str(data_key="message")
    r""" Message describing the current condition of chassis fans. It is only of use when `failed_fan.count` is not zero.

Example: There are no failed fans. """

    @property
    def resource(self):
        return NodeControllerFailedFanMessage

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


class NodeControllerFailedFanMessage(Resource):

    _schema = NodeControllerFailedFanMessageSchema
