r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LdapStatus", "LdapStatusSchema"]
__pdoc__ = {
    "LdapStatusSchema.resource": False,
    "LdapStatus": False,
}


class LdapStatusSchema(ResourceSchema):
    """The fields of the LdapStatus object"""

    code = Size(data_key="code")
    r""" Code corresponding to the status message.


Example: 65537300 """

    dn_message = fields.List(fields.Str, data_key="dn_message")
    r""" The dn_message field of the ldap_status. """

    message = fields.Str(data_key="message")
    r""" Provides additional details on the status of the LDAP service. """

    state = fields.Str(data_key="state")
    r""" Specifies the status of the LDAP service.


Valid choices:

* up
* down """

    @property
    def resource(self):
        return LdapStatus

    gettable_fields = [
        "code",
        "dn_message",
        "message",
        "state",
    ]
    """code,dn_message,message,state,"""

    patchable_fields = [
        "code",
        "dn_message",
        "message",
        "state",
    ]
    """code,dn_message,message,state,"""

    postable_fields = [
        "code",
        "dn_message",
        "message",
        "state",
    ]
    """code,dn_message,message,state,"""


class LdapStatus(Resource):

    _schema = LdapStatusSchema
