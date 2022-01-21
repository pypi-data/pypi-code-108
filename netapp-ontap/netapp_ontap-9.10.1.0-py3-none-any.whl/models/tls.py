r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Tls", "TlsSchema"]
__pdoc__ = {
    "TlsSchema.resource": False,
    "Tls": False,
}


class TlsSchema(ResourceSchema):
    """The fields of the Tls object"""

    cipher_suites = fields.List(fields.Str, data_key="cipher_suites")
    r""" Names a cipher suite that the system can select during TLS handshakes. A list of available options can be found on the Internet Assigned Number Authority (IANA) website. """

    protocol_versions = fields.List(fields.Str, data_key="protocol_versions")
    r""" Names a TLS protocol version that the system can select during TLS handshakes. The use of SSLv3 or TLSv1 is discouraged. """

    @property
    def resource(self):
        return Tls

    gettable_fields = [
        "cipher_suites",
        "protocol_versions",
    ]
    """cipher_suites,protocol_versions,"""

    patchable_fields = [
        "cipher_suites",
        "protocol_versions",
    ]
    """cipher_suites,protocol_versions,"""

    postable_fields = [
        "cipher_suites",
        "protocol_versions",
    ]
    """cipher_suites,protocol_versions,"""


class Tls(Resource):

    _schema = TlsSchema
