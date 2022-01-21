r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ExportRules", "ExportRulesSchema"]
__pdoc__ = {
    "ExportRulesSchema.resource": False,
    "ExportRules": False,
}


class ExportRulesSchema(ResourceSchema):
    """The fields of the ExportRules object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the export_rules. """

    allow_device_creation = fields.Boolean(data_key="allow_device_creation")
    r""" Specifies whether or not device creation is allowed. """

    allow_suid = fields.Boolean(data_key="allow_suid")
    r""" Specifies whether or not SetUID bits in SETATTR Op is to be honored. """

    anonymous_user = fields.Str(data_key="anonymous_user")
    r""" User ID To Which Anonymous Users Are Mapped. """

    chown_mode = fields.Str(data_key="chown_mode")
    r""" Specifies who is authorized to change the ownership mode of a file.

Valid choices:

* restricted
* unrestricted """

    clients = fields.List(fields.Nested("netapp_ontap.models.export_clients.ExportClientsSchema", unknown=EXCLUDE), data_key="clients")
    r""" Array of client matches """

    index = Size(data_key="index")
    r""" Index of the rule within the export policy. """

    ntfs_unix_security = fields.Str(data_key="ntfs_unix_security")
    r""" NTFS export UNIX security options.

Valid choices:

* fail
* ignore """

    protocols = fields.List(fields.Str, data_key="protocols")
    r""" The protocols field of the export_rules. """

    ro_rule = fields.List(fields.Str, data_key="ro_rule")
    r""" Authentication flavors that the read-only access rule governs """

    rw_rule = fields.List(fields.Str, data_key="rw_rule")
    r""" Authentication flavors that the read/write access rule governs """

    superuser = fields.List(fields.Str, data_key="superuser")
    r""" Authentication flavors that the superuser security type governs """

    @property
    def resource(self):
        return ExportRules

    gettable_fields = [
        "links",
        "allow_device_creation",
        "allow_suid",
        "anonymous_user",
        "chown_mode",
        "clients",
        "index",
        "ntfs_unix_security",
        "protocols",
        "ro_rule",
        "rw_rule",
        "superuser",
    ]
    """links,allow_device_creation,allow_suid,anonymous_user,chown_mode,clients,index,ntfs_unix_security,protocols,ro_rule,rw_rule,superuser,"""

    patchable_fields = [
        "allow_device_creation",
        "allow_suid",
        "anonymous_user",
        "chown_mode",
        "clients",
        "ntfs_unix_security",
        "protocols",
        "ro_rule",
        "rw_rule",
        "superuser",
    ]
    """allow_device_creation,allow_suid,anonymous_user,chown_mode,clients,ntfs_unix_security,protocols,ro_rule,rw_rule,superuser,"""

    postable_fields = [
        "allow_device_creation",
        "allow_suid",
        "anonymous_user",
        "chown_mode",
        "clients",
        "ntfs_unix_security",
        "protocols",
        "ro_rule",
        "rw_rule",
        "superuser",
    ]
    """allow_device_creation,allow_suid,anonymous_user,chown_mode,clients,ntfs_unix_security,protocols,ro_rule,rw_rule,superuser,"""


class ExportRules(Resource):

    _schema = ExportRulesSchema
