r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Status", "StatusSchema"]
__pdoc__ = {
    "StatusSchema.resource": False,
    "Status": False,
}


class StatusSchema(ResourceSchema):
    """The fields of the Status object"""

    code = Size(data_key="code")
    r""" Code corresponding to the status message. Code is 0 when the state is 'up'.


Example: 6684732 """

    message = fields.Str(data_key="message")
    r""" Detailed description of the validation state if the state is 'down' or
the response time of the DNS server if the state is 'up'. """

    name_server = fields.Str(data_key="name_server")
    r""" The IP address of the DNS server. The address can be either an IPv4 or an IPv6 address.


Example: 10.10.10.10 """

    state = fields.Str(data_key="state")
    r""" The validation status of the DNS server.


Valid choices:

* up
* down """

    @property
    def resource(self):
        return Status

    gettable_fields = [
        "code",
        "message",
        "name_server",
        "state",
    ]
    """code,message,name_server,state,"""

    patchable_fields = [
        "code",
        "message",
        "name_server",
        "state",
    ]
    """code,message,name_server,state,"""

    postable_fields = [
        "code",
        "message",
        "name_server",
        "state",
    ]
    """code,message,name_server,state,"""


class Status(Resource):

    _schema = StatusSchema
