r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["OnboardKeyManagerConfigurableStatus", "OnboardKeyManagerConfigurableStatusSchema"]
__pdoc__ = {
    "OnboardKeyManagerConfigurableStatusSchema.resource": False,
    "OnboardKeyManagerConfigurableStatus": False,
}


class OnboardKeyManagerConfigurableStatusSchema(ResourceSchema):
    """The fields of the OnboardKeyManagerConfigurableStatus object"""

    code = Size(data_key="code")
    r""" Code corresponding to the status message. Returns a 0 if the Onboard Key Manager can be configured in the cluster.

Example: 65537300 """

    message = fields.Str(data_key="message")
    r""" Reason that Onboard Key Manager cannot be configured in the cluster.

Example: No platform support for volume encryption in following nodes - node1, node2. """

    supported = fields.Boolean(data_key="supported")
    r""" Set to true if the Onboard Key Manager can be configured in the cluster. """

    @property
    def resource(self):
        return OnboardKeyManagerConfigurableStatus

    gettable_fields = [
        "code",
        "message",
        "supported",
    ]
    """code,message,supported,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class OnboardKeyManagerConfigurableStatus(Resource):

    _schema = OnboardKeyManagerConfigurableStatusSchema
