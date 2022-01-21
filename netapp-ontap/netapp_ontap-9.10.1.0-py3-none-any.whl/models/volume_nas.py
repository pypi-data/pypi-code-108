r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeNas", "VolumeNasSchema"]
__pdoc__ = {
    "VolumeNasSchema.resource": False,
    "VolumeNas": False,
}


class VolumeNasSchema(ResourceSchema):
    """The fields of the VolumeNas object"""

    export_policy = fields.Nested("netapp_ontap.resources.export_policy.ExportPolicySchema", unknown=EXCLUDE, data_key="export_policy")
    r""" The export_policy field of the volume_nas. """

    gid = Size(data_key="gid")
    r""" The UNIX group ID of the volume. Valid in POST or PATCH. """

    junction_parent = fields.Nested("netapp_ontap.models.volume_nas_junction_parent.VolumeNasJunctionParentSchema", unknown=EXCLUDE, data_key="junction_parent")
    r""" The junction_parent field of the volume_nas. """

    path = fields.Str(data_key="path")
    r""" The fully-qualified path in the owning SVM's namespace at which the volume is mounted. The path is case insensitive and must be unique within a SVM's namespace. Path must begin with '/' and must not end with '/'. Only one volume can be mounted at any given junction path. An empty path in POST creates an unmounted volume. An empty path in PATCH deactivates and unmounts the volume. Taking a volume offline or restricted state removes its junction path. This attribute is reported in GET only when the volume is mounted.

Example: /user/my_volume """

    security_style = fields.Str(data_key="security_style")
    r""" Security style associated with the volume. Valid in POST or PATCH.<br>mixed &dash; Mixed-style security<br>ntfs &dash; NTFS/WIndows-style security<br>unified &dash; Unified-style security, unified UNIX, NFS and CIFS permissions<br>unix &dash; Unix-style security.

Valid choices:

* mixed
* ntfs
* unified
* unix """

    uid = Size(data_key="uid")
    r""" The UNIX user ID of the volume. Valid in POST or PATCH. """

    unix_permissions = Size(data_key="unix_permissions")
    r""" UNIX permissions to be viewed as an octal number. It consists of 4 digits derived by adding up bits 4 (read), 2 (write) and 1 (execute). First digit selects the set user ID(4), set group ID (2) and sticky (1) attributes. The second digit selects permission for the owner of the file; the third selects permissions for other users in the same group; the fourth for other users not in the group. Valid in POST or PATCH. For security style "mixed" or "unix", the default setting is 0755 in octal (493 in decimal) and for security style "ntfs", the default setting is 0000. In cases where only owner, group and other permissions are given (as in 755, representing the second, third and fourth dight), first digit is assumed to be zero.

Example: 493 """

    @property
    def resource(self):
        return VolumeNas

    gettable_fields = [
        "export_policy.links",
        "export_policy.id",
        "export_policy.name",
        "gid",
        "junction_parent",
        "path",
        "security_style",
        "uid",
        "unix_permissions",
    ]
    """export_policy.links,export_policy.id,export_policy.name,gid,junction_parent,path,security_style,uid,unix_permissions,"""

    patchable_fields = [
        "export_policy.id",
        "export_policy.name",
        "gid",
        "junction_parent",
        "path",
        "security_style",
        "uid",
        "unix_permissions",
    ]
    """export_policy.id,export_policy.name,gid,junction_parent,path,security_style,uid,unix_permissions,"""

    postable_fields = [
        "export_policy.id",
        "export_policy.name",
        "gid",
        "junction_parent",
        "path",
        "security_style",
        "uid",
        "unix_permissions",
    ]
    """export_policy.id,export_policy.name,gid,junction_parent,path,security_style,uid,unix_permissions,"""


class VolumeNas(Resource):

    _schema = VolumeNasSchema
