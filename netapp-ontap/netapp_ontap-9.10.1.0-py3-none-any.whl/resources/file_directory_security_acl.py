r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

import asyncio
from datetime import datetime
import inspect
from typing import Callable, Iterable, List, Optional, Union

try:
    RECLINE_INSTALLED = False
    import recline
    from recline.arg_types.choices import Choices
    from recline.commands import ClicheCommandError
    from netapp_ontap.resource_table import ResourceTable
    RECLINE_INSTALLED = True
except ImportError:
    pass

from marshmallow import fields, EXCLUDE  # type: ignore

import netapp_ontap
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size
from netapp_ontap import NetAppResponse, HostConnection
from netapp_ontap.validations import enum_validation, len_validation, integer_validation
from netapp_ontap.error import NetAppRestError


__all__ = ["FileDirectorySecurityAcl", "FileDirectorySecurityAclSchema"]
__pdoc__ = {
    "FileDirectorySecurityAclSchema.resource": False,
    "FileDirectorySecurityAcl.file_directory_security_acl_show": False,
    "FileDirectorySecurityAcl.file_directory_security_acl_create": False,
    "FileDirectorySecurityAcl.file_directory_security_acl_modify": False,
    "FileDirectorySecurityAcl.file_directory_security_acl_delete": False,
}


class FileDirectorySecurityAclSchema(ResourceSchema):
    """The fields of the FileDirectorySecurityAcl object"""

    access = fields.Str(
        data_key="access",
        validate=enum_validation(['access_allow', 'access_deny', 'audit_failure', 'audit_success']),
    )
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

    access_control = fields.Str(
        data_key="access_control",
        validate=enum_validation(['file_directory', 'slag']),
    )
    r""" Access Control Level specifies the access control of the task to be applied. Valid values
are "file-directory" or "Storage-Level Access Guard (SLAG)". SLAG is used to apply the
specified security descriptors with the task for the volume or qtree. Otherwise, the
security descriptors are applied on files and directories at the specified path. The
value slag is not supported on FlexGroups volumes. The default value is "file-directory".


Valid choices:

* file_directory
* slag """

    advanced_rights = fields.Nested("netapp_ontap.models.advanced_rights.AdvancedRightsSchema", data_key="advanced_rights", unknown=EXCLUDE)
    r""" The advanced_rights field of the file_directory_security_acl. """

    apply_to = fields.Nested("netapp_ontap.models.apply_to.ApplyToSchema", data_key="apply_to", unknown=EXCLUDE)
    r""" The apply_to field of the file_directory_security_acl. """

    ignore_paths = fields.List(fields.Str, data_key="ignore_paths")
    r""" Specifies that permissions on this file or directory cannot be replaced.


Example: ["/dir1/dir2/","/parent/dir3"] """

    propagation_mode = fields.Str(
        data_key="propagation_mode",
        validate=enum_validation(['propagate', 'replace']),
    )
    r""" Specifies how to propagate security settings to child subfolders and files.
This setting determines how child files/folders contained within a parent
folder inherit access control and audit information from the parent folder.
The available values are:

* propogate    - propagate inheritable permissions to all subfolders and files
* replace      - replace existing permissions on all subfolders and files with inheritable permissions


Valid choices:

* propagate
* replace """

    rights = fields.Str(
        data_key="rights",
        validate=enum_validation(['no_access', 'full_control', 'modify', 'read_and_execute', 'read', 'write']),
    )
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

    user = fields.Str(
        data_key="user",
    )
    r""" Specifies the account to which the ACE applies.
You can specify either name or SID.


Example: S-1-5-21-2233347455-2266964949-1780268902-69304 """

    @property
    def resource(self):
        return FileDirectorySecurityAcl

    gettable_fields = [
        "access",
        "access_control",
        "advanced_rights",
        "apply_to",
        "ignore_paths",
        "propagation_mode",
        "rights",
        "user",
    ]
    """access,access_control,advanced_rights,apply_to,ignore_paths,propagation_mode,rights,user,"""

    patchable_fields = [
        "access",
        "access_control",
        "advanced_rights",
        "apply_to",
        "ignore_paths",
        "propagation_mode",
        "rights",
    ]
    """access,access_control,advanced_rights,apply_to,ignore_paths,propagation_mode,rights,"""

    postable_fields = [
        "access",
        "access_control",
        "advanced_rights",
        "apply_to",
        "ignore_paths",
        "propagation_mode",
        "rights",
        "user",
    ]
    """access,access_control,advanced_rights,apply_to,ignore_paths,propagation_mode,rights,user,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FileDirectorySecurityAcl.get_collection(fields=field)]
    return getter

async def _wait_for_job(response: NetAppResponse) -> None:
    """Examine the given response. If it is a job, asynchronously wait for it to
    complete. While polling, prints the current status message of the job.
    """

    if not response.is_job:
        return
    from netapp_ontap.resources import Job
    job = Job(**response.http_response.json()["job"])
    while True:
        job.get(fields="state,message")
        if hasattr(job, "message"):
            print("[%s]: %s" % (job.state, job.message))
        if job.state == "failure":
            raise NetAppRestError("FileDirectorySecurityAcl modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FileDirectorySecurityAcl(Resource):
    r""" Manages the DACLS or SACLS. """

    _schema = FileDirectorySecurityAclSchema
    _path = "/api/protocols/file-security/permissions/{svm[uuid]}/{file_directory_security[path]}/acl"
    _keys = ["svm.uuid", "file_directory_security.path", "user"]



    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["FileDirectorySecurityAcl"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the SACLs/DACLs
You must keep the following points in mind while using these endpoints:
* SLAG applies to all files and/or directories in a volume hence, inheritance is not required to be propagated.
* Set access_control field to slag while updating SLAG ACE.
* Set access_control field to file_directory while updating file-directory ACE. By Default access_control field is set to file_directory.
* For SLAG, valid apply_to combinations are "this-folder, sub-folders", "files", "this-folder, sub-folders, files".
### Related ONTAP commands
* `vserver security file-directory ntfs dacl modify`
* `vserver security file-directory ntfs sacl modify`
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["FileDirectorySecurityAcl"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["FileDirectorySecurityAcl"], NetAppResponse]:
        r"""Adds the new SACL/DACL ACE.
You must keep the following points in mind while using these endpoints:
* SLAG applies to all files and/or directories in a volume hence, inheritance is not required to be propagated.
* Set access_control field to slag while adding SLAG ACE.
* Set access_control field to file_directory while adding file-directory ACE. By Default access_control field is set to file_directory.
* For SLAG, valid apply_to combinations are "this-folder, sub-folders", "files", "this-folder, sub-folders, files".
### Related ONTAP commands
* `vserver security file-directory ntfs dacl add`
* `vserver security file-directory ntfs sacl add`
"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["FileDirectorySecurityAcl"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the SACL/DACL ACL
You must keep the following points in mind while using these endpoints:
* SLAG applies to all files and/or directories in a volume hence, inheritance is not required to be propagated.
* Set access_control field to slag while deleting SLAG ACE.
* Set access_control field to file_directory while deleting file-directory ACE. By Default access_control field is set to file_directory.
* For SLAG, valid apply_to combinations are "this-folder, sub-folders", "files", "this-folder, sub-folders, files".
### Related ONTAP commands
* `vserver security file-directory ntfs dacl remove`
* `vserver security file-directory ntfs sacl remove`
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)



    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Adds the new SACL/DACL ACE.
You must keep the following points in mind while using these endpoints:
* SLAG applies to all files and/or directories in a volume hence, inheritance is not required to be propagated.
* Set access_control field to slag while adding SLAG ACE.
* Set access_control field to file_directory while adding file-directory ACE. By Default access_control field is set to file_directory.
* For SLAG, valid apply_to combinations are "this-folder, sub-folders", "files", "this-folder, sub-folders, files".
### Related ONTAP commands
* `vserver security file-directory ntfs dacl add`
* `vserver security file-directory ntfs sacl add`
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file directory security acl create")
        async def file_directory_security_acl_create(
            path,
            svm_uuid,
            access: str = None,
            access_control: str = None,
            advanced_rights: dict = None,
            apply_to: dict = None,
            ignore_paths = None,
            propagation_mode: str = None,
            rights: str = None,
            user: str = None,
        ) -> ResourceTable:
            """Create an instance of a FileDirectorySecurityAcl resource

            Args:
                access: Specifies whether the ACL is for DACL or SACL. The available values are: * access_allow                     - DACL for allow access * access_deny                      - DACL for deny access * audit_success                    - SACL for success access * audit_failure                    - SACL for failure access 
                access_control: Access Control Level specifies the access control of the task to be applied. Valid values are \"file-directory\" or \"Storage-Level Access Guard (SLAG)\". SLAG is used to apply the specified security descriptors with the task for the volume or qtree. Otherwise, the security descriptors are applied on files and directories at the specified path. The value slag is not supported on FlexGroups volumes. The default value is \"file-directory\". 
                advanced_rights: 
                apply_to: 
                ignore_paths: Specifies that permissions on this file or directory cannot be replaced. 
                propagation_mode: Specifies how to propagate security settings to child subfolders and files. This setting determines how child files/folders contained within a parent folder inherit access control and audit information from the parent folder. The available values are: * propogate    - propagate inheritable permissions to all subfolders and files * replace      - replace existing permissions on all subfolders and files with inheritable permissions 
                rights: Specifies the access right controlled by the ACE for the account specified. The \"rights\" parameter is mutually exclusive with the \"advanced_rights\" parameter. If you specify the \"rights\" parameter, you can specify one of the following \"rights\" values: 
                user: Specifies the account to which the ACE applies. You can specify either name or SID. 
            """

            kwargs = {}
            if access is not None:
                kwargs["access"] = access
            if access_control is not None:
                kwargs["access_control"] = access_control
            if advanced_rights is not None:
                kwargs["advanced_rights"] = advanced_rights
            if apply_to is not None:
                kwargs["apply_to"] = apply_to
            if ignore_paths is not None:
                kwargs["ignore_paths"] = ignore_paths
            if propagation_mode is not None:
                kwargs["propagation_mode"] = propagation_mode
            if rights is not None:
                kwargs["rights"] = rights
            if user is not None:
                kwargs["user"] = user

            resource = FileDirectorySecurityAcl(
                path,
                svm_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create FileDirectorySecurityAcl: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the SACLs/DACLs
You must keep the following points in mind while using these endpoints:
* SLAG applies to all files and/or directories in a volume hence, inheritance is not required to be propagated.
* Set access_control field to slag while updating SLAG ACE.
* Set access_control field to file_directory while updating file-directory ACE. By Default access_control field is set to file_directory.
* For SLAG, valid apply_to combinations are "this-folder, sub-folders", "files", "this-folder, sub-folders, files".
### Related ONTAP commands
* `vserver security file-directory ntfs dacl modify`
* `vserver security file-directory ntfs sacl modify`
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file directory security acl modify")
        async def file_directory_security_acl_modify(
            path,
            svm_uuid,
            access: str = None,
            query_access: str = None,
            access_control: str = None,
            query_access_control: str = None,
            ignore_paths=None,
            query_ignore_paths=None,
            propagation_mode: str = None,
            query_propagation_mode: str = None,
            rights: str = None,
            query_rights: str = None,
            user: str = None,
            query_user: str = None,
        ) -> ResourceTable:
            """Modify an instance of a FileDirectorySecurityAcl resource

            Args:
                access: Specifies whether the ACL is for DACL or SACL. The available values are: * access_allow                     - DACL for allow access * access_deny                      - DACL for deny access * audit_success                    - SACL for success access * audit_failure                    - SACL for failure access 
                query_access: Specifies whether the ACL is for DACL or SACL. The available values are: * access_allow                     - DACL for allow access * access_deny                      - DACL for deny access * audit_success                    - SACL for success access * audit_failure                    - SACL for failure access 
                access_control: Access Control Level specifies the access control of the task to be applied. Valid values are \"file-directory\" or \"Storage-Level Access Guard (SLAG)\". SLAG is used to apply the specified security descriptors with the task for the volume or qtree. Otherwise, the security descriptors are applied on files and directories at the specified path. The value slag is not supported on FlexGroups volumes. The default value is \"file-directory\". 
                query_access_control: Access Control Level specifies the access control of the task to be applied. Valid values are \"file-directory\" or \"Storage-Level Access Guard (SLAG)\". SLAG is used to apply the specified security descriptors with the task for the volume or qtree. Otherwise, the security descriptors are applied on files and directories at the specified path. The value slag is not supported on FlexGroups volumes. The default value is \"file-directory\". 
                ignore_paths: Specifies that permissions on this file or directory cannot be replaced. 
                query_ignore_paths: Specifies that permissions on this file or directory cannot be replaced. 
                propagation_mode: Specifies how to propagate security settings to child subfolders and files. This setting determines how child files/folders contained within a parent folder inherit access control and audit information from the parent folder. The available values are: * propogate    - propagate inheritable permissions to all subfolders and files * replace      - replace existing permissions on all subfolders and files with inheritable permissions 
                query_propagation_mode: Specifies how to propagate security settings to child subfolders and files. This setting determines how child files/folders contained within a parent folder inherit access control and audit information from the parent folder. The available values are: * propogate    - propagate inheritable permissions to all subfolders and files * replace      - replace existing permissions on all subfolders and files with inheritable permissions 
                rights: Specifies the access right controlled by the ACE for the account specified. The \"rights\" parameter is mutually exclusive with the \"advanced_rights\" parameter. If you specify the \"rights\" parameter, you can specify one of the following \"rights\" values: 
                query_rights: Specifies the access right controlled by the ACE for the account specified. The \"rights\" parameter is mutually exclusive with the \"advanced_rights\" parameter. If you specify the \"rights\" parameter, you can specify one of the following \"rights\" values: 
                user: Specifies the account to which the ACE applies. You can specify either name or SID. 
                query_user: Specifies the account to which the ACE applies. You can specify either name or SID. 
            """

            kwargs = {}
            changes = {}
            if query_access is not None:
                kwargs["access"] = query_access
            if query_access_control is not None:
                kwargs["access_control"] = query_access_control
            if query_ignore_paths is not None:
                kwargs["ignore_paths"] = query_ignore_paths
            if query_propagation_mode is not None:
                kwargs["propagation_mode"] = query_propagation_mode
            if query_rights is not None:
                kwargs["rights"] = query_rights
            if query_user is not None:
                kwargs["user"] = query_user

            if access is not None:
                changes["access"] = access
            if access_control is not None:
                changes["access_control"] = access_control
            if ignore_paths is not None:
                changes["ignore_paths"] = ignore_paths
            if propagation_mode is not None:
                changes["propagation_mode"] = propagation_mode
            if rights is not None:
                changes["rights"] = rights
            if user is not None:
                changes["user"] = user

            if hasattr(FileDirectorySecurityAcl, "find"):
                resource = FileDirectorySecurityAcl.find(
                    path,
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = FileDirectorySecurityAcl(path,svm_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify FileDirectorySecurityAcl: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the SACL/DACL ACL
You must keep the following points in mind while using these endpoints:
* SLAG applies to all files and/or directories in a volume hence, inheritance is not required to be propagated.
* Set access_control field to slag while deleting SLAG ACE.
* Set access_control field to file_directory while deleting file-directory ACE. By Default access_control field is set to file_directory.
* For SLAG, valid apply_to combinations are "this-folder, sub-folders", "files", "this-folder, sub-folders, files".
### Related ONTAP commands
* `vserver security file-directory ntfs dacl remove`
* `vserver security file-directory ntfs sacl remove`
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file directory security acl delete")
        async def file_directory_security_acl_delete(
            path,
            svm_uuid,
            access: str = None,
            access_control: str = None,
            ignore_paths=None,
            propagation_mode: str = None,
            rights: str = None,
            user: str = None,
        ) -> None:
            """Delete an instance of a FileDirectorySecurityAcl resource

            Args:
                access: Specifies whether the ACL is for DACL or SACL. The available values are: * access_allow                     - DACL for allow access * access_deny                      - DACL for deny access * audit_success                    - SACL for success access * audit_failure                    - SACL for failure access 
                access_control: Access Control Level specifies the access control of the task to be applied. Valid values are \"file-directory\" or \"Storage-Level Access Guard (SLAG)\". SLAG is used to apply the specified security descriptors with the task for the volume or qtree. Otherwise, the security descriptors are applied on files and directories at the specified path. The value slag is not supported on FlexGroups volumes. The default value is \"file-directory\". 
                ignore_paths: Specifies that permissions on this file or directory cannot be replaced. 
                propagation_mode: Specifies how to propagate security settings to child subfolders and files. This setting determines how child files/folders contained within a parent folder inherit access control and audit information from the parent folder. The available values are: * propogate    - propagate inheritable permissions to all subfolders and files * replace      - replace existing permissions on all subfolders and files with inheritable permissions 
                rights: Specifies the access right controlled by the ACE for the account specified. The \"rights\" parameter is mutually exclusive with the \"advanced_rights\" parameter. If you specify the \"rights\" parameter, you can specify one of the following \"rights\" values: 
                user: Specifies the account to which the ACE applies. You can specify either name or SID. 
            """

            kwargs = {}
            if access is not None:
                kwargs["access"] = access
            if access_control is not None:
                kwargs["access_control"] = access_control
            if ignore_paths is not None:
                kwargs["ignore_paths"] = ignore_paths
            if propagation_mode is not None:
                kwargs["propagation_mode"] = propagation_mode
            if rights is not None:
                kwargs["rights"] = rights
            if user is not None:
                kwargs["user"] = user

            if hasattr(FileDirectorySecurityAcl, "find"):
                resource = FileDirectorySecurityAcl.find(
                    path,
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = FileDirectorySecurityAcl(path,svm_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete FileDirectorySecurityAcl: %s" % err)


