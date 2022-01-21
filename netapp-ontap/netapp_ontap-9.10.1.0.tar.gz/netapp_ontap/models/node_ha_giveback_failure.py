r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeHaGivebackFailure", "NodeHaGivebackFailureSchema"]
__pdoc__ = {
    "NodeHaGivebackFailureSchema.resource": False,
    "NodeHaGivebackFailure": False,
}


class NodeHaGivebackFailureSchema(ResourceSchema):
    """The fields of the NodeHaGivebackFailure object"""

    code = Size(data_key="code")
    r""" Message code

Example: 852126 """

    message = fields.Str(data_key="message")
    r""" Detailed message based on the state.

Example: Failed to initiate giveback. Run the "storage failover show-giveback" command for more information. """

    @property
    def resource(self):
        return NodeHaGivebackFailure

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


class NodeHaGivebackFailure(Resource):

    _schema = NodeHaGivebackFailureSchema
