r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ManagementProtocols", "ManagementProtocolsSchema"]
__pdoc__ = {
    "ManagementProtocolsSchema.resource": False,
    "ManagementProtocols": False,
}


class ManagementProtocolsSchema(ResourceSchema):
    """The fields of the ManagementProtocols object"""

    rsh_enabled = fields.Boolean(data_key="rsh_enabled")
    r""" Indicates whether or not security protocol rsh is enabled on the cluster. """

    telnet_enabled = fields.Boolean(data_key="telnet_enabled")
    r""" Indicates whether or not security protocol telnet is enabled on the cluster. """

    @property
    def resource(self):
        return ManagementProtocols

    gettable_fields = [
        "rsh_enabled",
        "telnet_enabled",
    ]
    """rsh_enabled,telnet_enabled,"""

    patchable_fields = [
        "rsh_enabled",
        "telnet_enabled",
    ]
    """rsh_enabled,telnet_enabled,"""

    postable_fields = [
    ]
    """"""


class ManagementProtocols(Resource):

    _schema = ManagementProtocolsSchema
