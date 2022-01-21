r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeHaTakeoverFailure", "NodeHaTakeoverFailureSchema"]
__pdoc__ = {
    "NodeHaTakeoverFailureSchema.resource": False,
    "NodeHaTakeoverFailure": False,
}


class NodeHaTakeoverFailureSchema(ResourceSchema):
    """The fields of the NodeHaTakeoverFailure object"""

    code = Size(data_key="code")
    r""" Message code

Example: 852130 """

    message = fields.Str(data_key="message")
    r""" Detailed message based on the state.

Example: Failed to initiate takeover. Run the "storage failover show-takeover" command for more information. """

    @property
    def resource(self):
        return NodeHaTakeoverFailure

    gettable_fields = [
        "code",
        "message",
    ]
    """code,message,"""

    patchable_fields = [
        "code",
        "message",
    ]
    """code,message,"""

    postable_fields = [
        "code",
        "message",
    ]
    """code,message,"""


class NodeHaTakeoverFailure(Resource):

    _schema = NodeHaTakeoverFailureSchema
