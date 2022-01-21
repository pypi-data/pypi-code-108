r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Acl", "AclSchema"]
__pdoc__ = {
    "AclSchema.resource": False,
    "Acl": False,
}


class AclSchema(ResourceSchema):
    """The fields of the Acl object"""

    access = fields.Str(data_key="access")
    r""" Specifies whether the ACL is for DACL or SACL.
The available values are:

* access_allow                     - DACL for allow access
* access_deny                      - DACL for deny access
* access_allowed_callback          - CALLBACK for allowed access
* access_denied_callback           - CALLBACK for denied access
* access_allowed_callback_object   - CALLBACK OBJECT for allowed access
* access_denied_callback_object    - CALLBACK OBJECT for denied access
* system_audit_callback            - SYSTEM Audit Callback ace
* system_audit_callback_object     - SYSTEM Audit Callback Object ace
* system_resource_attribute        - SYSTEM Resource Attribute
* system_scoped_policy_id          - SYSTEM Scope Policy ID
* audit_success                    - SACL for success access
* audit_failure                    - SACL for failure access
* audit_success_and_failure        - SACL for both success and failure access


Valid choices:

* access_allow
* access_deny
* access_allowed_callback
* access_denied_callback
* access_allowed_callback_object
* access_denied_callback_object
* system_audit_callback
* system_audit_callback_object
* system_resource_attribute
* system_scoped_policy_id
* audit_failure
* audit_success
* audit_success_and_failure """

    access_control = fields.Str(data_key="access_control")
    r""" An Access Control Level specifies the access control of the task to be applied. Valid values
are "file-directory" or "Storage-Level Access Guard (SLAG)". SLAG is used to apply the
specified security descriptors with the task for the volume or qtree. Otherwise, the security
descriptors are applied on files and directories at the specified path. The value slag is not
supported on FlexGroups volumes. The default value is "file-directory".


Valid choices:

* file_directory
* slag """

    advanced_rights = fields.Nested("netapp_ontap.models.advanced_rights.AdvancedRightsSchema", unknown=EXCLUDE, data_key="advanced_rights")
    r""" The advanced_rights field of the acl. """

    apply_to = fields.Nested("netapp_ontap.models.apply_to.ApplyToSchema", unknown=EXCLUDE, data_key="apply_to")
    r""" The apply_to field of the acl. """

    inherited = fields.Boolean(data_key="inherited")
    r""" Indicates whether or not the ACE flag is inherited.


Example: true """

    rights = fields.Str(data_key="rights")
    r""" Specifies the access right controlled by the ACE for the account specified.
The "rights" parameter is mutually exclusive with the "advanced_rights"
parameter. If you specify the "rights" parameter, you can specify one
of the following "rights" values:


Valid choices:

* no_access
* full_control
* modify
* read_and_execute
* read
* write """

    user = fields.Str(data_key="user")
    r""" Specifies the account to which the ACE applies.
You can specify either name or SID.


Example: S-1-5-21-2233347455-2266964949-1780268902-69304 """

    @property
    def resource(self):
        return Acl

    gettable_fields = [
        "access",
        "access_control",
        "advanced_rights",
        "apply_to",
        "inherited",
        "rights",
        "user",
    ]
    """access,access_control,advanced_rights,apply_to,inherited,rights,user,"""

    patchable_fields = [
        "access",
        "advanced_rights",
        "apply_to",
        "rights",
    ]
    """access,advanced_rights,apply_to,rights,"""

    postable_fields = [
        "access",
        "advanced_rights",
        "apply_to",
        "rights",
        "user",
    ]
    """access,advanced_rights,apply_to,rights,user,"""


class Acl(Resource):

    _schema = AclSchema
