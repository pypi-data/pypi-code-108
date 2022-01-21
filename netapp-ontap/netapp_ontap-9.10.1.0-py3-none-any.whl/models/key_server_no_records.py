r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["KeyServerNoRecords", "KeyServerNoRecordsSchema"]
__pdoc__ = {
    "KeyServerNoRecordsSchema.resource": False,
    "KeyServerNoRecords": False,
}


class KeyServerNoRecordsSchema(ResourceSchema):
    """The fields of the KeyServerNoRecords object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the key_server_no_records. """

    password = fields.Str(data_key="password")
    r""" Password credentials for connecting with the key server. This is not audited.

Example: password """

    secondary_key_servers = fields.List(fields.Str, data_key="secondary_key_servers")
    r""" A list of the secondary key servers associated with the primary key server. """

    server = fields.Str(data_key="server")
    r""" External key server for key management. If no port is provided, a default port of 5696 is used. Not valid in POST if `records` is provided.

Example: keyserver1.com:5698 """

    timeout = Size(data_key="timeout")
    r""" I/O timeout in seconds for communicating with the key server.

Example: 60 """

    username = fields.Str(data_key="username")
    r""" KMIP username credentials for connecting with the key server.

Example: username """

    @property
    def resource(self):
        return KeyServerNoRecords

    gettable_fields = [
        "links",
        "secondary_key_servers",
        "server",
        "timeout",
        "username",
    ]
    """links,secondary_key_servers,server,timeout,username,"""

    patchable_fields = [
        "password",
        "secondary_key_servers",
        "timeout",
        "username",
    ]
    """password,secondary_key_servers,timeout,username,"""

    postable_fields = [
        "secondary_key_servers",
        "server",
    ]
    """secondary_key_servers,server,"""


class KeyServerNoRecords(Resource):

    _schema = KeyServerNoRecordsSchema
