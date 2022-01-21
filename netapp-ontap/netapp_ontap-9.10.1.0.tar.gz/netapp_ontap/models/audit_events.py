r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AuditEvents", "AuditEventsSchema"]
__pdoc__ = {
    "AuditEventsSchema.resource": False,
    "AuditEvents": False,
}


class AuditEventsSchema(ResourceSchema):
    """The fields of the AuditEvents object"""

    authorization_policy = fields.Boolean(data_key="authorization_policy")
    r""" Authorization policy change events """

    cap_staging = fields.Boolean(data_key="cap_staging")
    r""" Central access policy staging events """

    cifs_logon_logoff = fields.Boolean(data_key="cifs_logon_logoff")
    r""" CIFS logon and logoff events """

    file_operations = fields.Boolean(data_key="file_operations")
    r""" File operation events """

    file_share = fields.Boolean(data_key="file_share")
    r""" File share category events """

    security_group = fields.Boolean(data_key="security_group")
    r""" Local security group management events """

    user_account = fields.Boolean(data_key="user_account")
    r""" Local user account management events """

    @property
    def resource(self):
        return AuditEvents

    gettable_fields = [
        "authorization_policy",
        "cap_staging",
        "cifs_logon_logoff",
        "file_operations",
        "file_share",
        "security_group",
        "user_account",
    ]
    """authorization_policy,cap_staging,cifs_logon_logoff,file_operations,file_share,security_group,user_account,"""

    patchable_fields = [
        "authorization_policy",
        "cap_staging",
        "cifs_logon_logoff",
        "file_operations",
        "file_share",
        "security_group",
        "user_account",
    ]
    """authorization_policy,cap_staging,cifs_logon_logoff,file_operations,file_share,security_group,user_account,"""

    postable_fields = [
        "authorization_policy",
        "cap_staging",
        "cifs_logon_logoff",
        "file_operations",
        "file_share",
        "security_group",
        "user_account",
    ]
    """authorization_policy,cap_staging,cifs_logon_logoff,file_operations,file_share,security_group,user_account,"""


class AuditEvents(Resource):

    _schema = AuditEventsSchema
