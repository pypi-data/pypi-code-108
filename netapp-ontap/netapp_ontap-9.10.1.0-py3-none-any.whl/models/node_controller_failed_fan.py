r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeControllerFailedFan", "NodeControllerFailedFanSchema"]
__pdoc__ = {
    "NodeControllerFailedFanSchema.resource": False,
    "NodeControllerFailedFan": False,
}


class NodeControllerFailedFanSchema(ResourceSchema):
    """The fields of the NodeControllerFailedFan object"""

    count = Size(data_key="count")
    r""" Specifies a count of the number of chassis fans that are not operating within the recommended RPM range.

Example: 1 """

    message = fields.Nested("netapp_ontap.models.node_controller_failed_fan_message.NodeControllerFailedFanMessageSchema", unknown=EXCLUDE, data_key="message")
    r""" The message field of the node_controller_failed_fan. """

    @property
    def resource(self):
        return NodeControllerFailedFan

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


class NodeControllerFailedFan(Resource):

    _schema = NodeControllerFailedFanSchema
