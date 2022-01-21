r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["KerberosRealmKdc", "KerberosRealmKdcSchema"]
__pdoc__ = {
    "KerberosRealmKdcSchema.resource": False,
    "KerberosRealmKdc": False,
}


class KerberosRealmKdcSchema(ResourceSchema):
    """The fields of the KerberosRealmKdc object"""

    ip = fields.Str(data_key="ip")
    r""" KDC IP address

Example: 1.2.3.4 """

    port = Size(data_key="port")
    r""" KDC port

Example: 88 """

    vendor = fields.Str(data_key="vendor")
    r""" Key Distribution Center (KDC) vendor. Following values are suported:

* microsoft - Microsoft Active Directory KDC
* other - MIT Kerberos KDC or other KDC


Valid choices:

* microsoft
* other """

    @property
    def resource(self):
        return KerberosRealmKdc

    gettable_fields = [
        "ip",
        "port",
        "vendor",
    ]
    """ip,port,vendor,"""

    patchable_fields = [
        "ip",
        "port",
        "vendor",
    ]
    """ip,port,vendor,"""

    postable_fields = [
        "ip",
        "port",
        "vendor",
    ]
    """ip,port,vendor,"""


class KerberosRealmKdc(Resource):

    _schema = KerberosRealmKdcSchema
