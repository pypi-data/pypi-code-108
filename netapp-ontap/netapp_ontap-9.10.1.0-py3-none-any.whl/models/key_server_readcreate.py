r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["KeyServerReadcreate", "KeyServerReadcreateSchema"]
__pdoc__ = {
    "KeyServerReadcreateSchema.resource": False,
    "KeyServerReadcreate": False,
}


class KeyServerReadcreateSchema(ResourceSchema):
    """The fields of the KeyServerReadcreate object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the key_server_readcreate. """

    secondary_key_servers = fields.List(fields.Str, data_key="secondary_key_servers")
    r""" A list of the secondary key servers associated with the primary key server. """

    server = fields.Str(data_key="server")
    r""" External key server for key management. If no port is provided, a default port of 5696 is used.

Example: keyserver1.com:5698 """

    timeout = Size(data_key="timeout")
    r""" I/O timeout in seconds for communicating with the key server.

Example: 60 """

    username = fields.Str(data_key="username")
    r""" Username credentials for connecting with the key server.

Example: admin """

    @property
    def resource(self):
        return KeyServerReadcreate

    gettable_fields = [
        "links",
        "secondary_key_servers",
        "server",
        "timeout",
        "username",
    ]
    """links,secondary_key_servers,server,timeout,username,"""

    patchable_fields = [
        "secondary_key_servers",
    ]
    """secondary_key_servers,"""

    postable_fields = [
        "secondary_key_servers",
        "server",
    ]
    """secondary_key_servers,server,"""


class KeyServerReadcreate(Resource):

    _schema = KeyServerReadcreateSchema
