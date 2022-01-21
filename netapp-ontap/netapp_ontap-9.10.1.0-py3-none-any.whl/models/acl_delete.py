r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AclDelete", "AclDeleteSchema"]
__pdoc__ = {
    "AclDeleteSchema.resource": False,
    "AclDelete": False,
}


class AclDeleteSchema(ResourceSchema):
    """The fields of the AclDelete object"""

    access = fields.Str(data_key="access")
    r""" Specifies whether the ACL is for DACL or SACL.
The available values are:

* access_allow                     - DACL for allow access
* access_deny                      - DACL for deny access
* audit_success                    - SACL for success access
* audit_failure                    - SACL for failure access


Valid choices:

* access_allow
* access_deny
* audit_failure
* audit_success """

    access_control = fields.Str(data_key="access_control")
    r""" An Access Control Level specifies the access control of the task to be applied. Valid values
are "file-directory" or "Storage-Level Access Guard (SLAG)". SLAG is used to apply the
specified security descriptors with the task for the volume or qtree. Otherwise, the
security descriptors are applied on files and directories at the specified path.
The value slag is not supported on FlexGroups volumes. The default value is "file-directory".


Valid choices:

* file_directory
* slag """

    apply_to = fields.Nested("netapp_ontap.models.apply_to.ApplyToSchema", unknown=EXCLUDE, data_key="apply_to")
    r""" The apply_to field of the acl_delete. """

    ignore_paths = fields.List(fields.Str, data_key="ignore_paths")
    r""" Specifies that permissions on this file or directory cannot be replaced.


Example: ["/dir1/dir2/","/parent/dir3"] """

    propagation_mode = fields.Str(data_key="propagation_mode")
    r""" Specifies how to propagate security settings to child subfolders and files.
This setting determines how child files/folders contained within a parent
folder inherit access control and audit information from the parent folder.
The available values are:

* propogate    - propagate inheritable permissions to all subfolders and files
* replace      - replace existing permissions on all subfolders and files with inheritable permissions


Valid choices:

* propagate
* replace """

    @property
    def resource(self):
        return AclDelete

    gettable_fields = [
        "access",
        "access_control",
        "apply_to",
        "ignore_paths",
        "propagation_mode",
    ]
    """access,access_control,apply_to,ignore_paths,propagation_mode,"""

    patchable_fields = [
        "access",
        "access_control",
        "apply_to",
        "ignore_paths",
        "propagation_mode",
    ]
    """access,access_control,apply_to,ignore_paths,propagation_mode,"""

    postable_fields = [
        "access",
        "access_control",
        "apply_to",
        "ignore_paths",
        "propagation_mode",
    ]
    """access,access_control,apply_to,ignore_paths,propagation_mode,"""


class AclDelete(Resource):

    _schema = AclDeleteSchema
