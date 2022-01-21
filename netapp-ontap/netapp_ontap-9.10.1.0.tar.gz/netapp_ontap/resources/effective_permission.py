r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
This API displays the effective permission granted to a Windows or UNIX user on the specified file or folder path.
## Examples
### Retrieving the effective permission for the specified Windows user on the specified path of an SVM.
```
# The API:
curl -X GET "https://10.63.26.252/api/protocols/file-security/effective-permissions/cf5f271a-1beb-11ea-8fad-005056bb645e/administrator/windows/%2F?share.name=sh1&return_records=true" -H "accept: application/json" -H "authorization: Basic YWRtaW46bmV0YXBwMSE="
# The response:
{
  "svm": {
    "uuid": "cf5f271a-1beb-11ea-8fad-005056bb645e",
    "name": "vs1"
  },
  "user": "administrator",
  "type": "windows",
  "path": "/",
  "share": {
    "path": "/"
  },
  "file_permission": [
    "read",
    "write",
    "append",
    "read_ea",
    "write_ea",
    "execute",
    "delete_child",
    "read_attributes",
    "write_attributes",
    "delete",
    "read_control",
    "write_dac",
    "write_owner",
    "synchronize",
    "system_security"
  ],
  "share_permission": [
    "read",
    "read_ea",
    "execute",
    "read_attributes",
    "read_control",
    "synchronize"
  ]
}
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


__all__ = ["EffectivePermission", "EffectivePermissionSchema"]
__pdoc__ = {
    "EffectivePermissionSchema.resource": False,
    "EffectivePermission.effective_permission_show": False,
    "EffectivePermission.effective_permission_create": False,
    "EffectivePermission.effective_permission_modify": False,
    "EffectivePermission.effective_permission_delete": False,
}


class EffectivePermissionSchema(ResourceSchema):
    """The fields of the EffectivePermission object"""

    file_permissions = fields.List(fields.Str, data_key="file_permissions")
    r""" Specifies the effective permission granted to a user on the specified file or folder path. """

    path = fields.Str(
        data_key="path",
    )
    r""" Specifies the path of the file or the folder for which you want to display effective permissions.
The path is relative to the SVM root volume. If "-share-name" is specified then path will be relative to the share path.


Example: /dir1/dir2 """

    share = fields.Nested("netapp_ontap.models.share.ShareSchema", data_key="share", unknown=EXCLUDE)
    r""" The share field of the effective_permission. """

    share_permissions = fields.List(fields.Str, data_key="share_permissions")
    r""" Specifies the effective permission granted to a user on the specified file or folder path. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the effective_permission. """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['windows', 'unix']),
    )
    r""" Specifies the user type. The following values are allowed:

* windows  - Windows user
* unix     - UNIX user


Valid choices:

* windows
* unix """

    user = fields.Str(
        data_key="user",
    )
    r""" Specifies the user for which effective permission needs to be displayed for the specified path.

Example: cifs1/administrator """

    @property
    def resource(self):
        return EffectivePermission

    gettable_fields = [
        "file_permissions",
        "path",
        "share",
        "share_permissions",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "type",
        "user",
    ]
    """file_permissions,path,share,share_permissions,svm.links,svm.name,svm.uuid,type,user,"""

    patchable_fields = [
        "file_permissions",
        "path",
        "share",
        "share_permissions",
        "svm.name",
        "svm.uuid",
        "type",
        "user",
    ]
    """file_permissions,path,share,share_permissions,svm.name,svm.uuid,type,user,"""

    postable_fields = [
        "file_permissions",
        "path",
        "share",
        "share_permissions",
        "svm.name",
        "svm.uuid",
        "type",
        "user",
    ]
    """file_permissions,path,share,share_permissions,svm.name,svm.uuid,type,user,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in EffectivePermission.get_collection(fields=field)]
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
            raise NetAppRestError("EffectivePermission modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class EffectivePermission(Resource):
    r""" Displays the effective permission granted to a Windows or UNIX user on the specified file or folder path. """

    _schema = EffectivePermissionSchema
    _path = "/api/protocols/file-security/effective-permissions"
    _keys = ["svm.uuid", "path"]







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves effective security permissions on a file.
### Related ONTAP commands
* `vserver security file-directory show-effective-permissions`

### Learn more
* [`DOC /protocols/file-security/effective-permissions/{svm.uuid}/{path}`](#docs-NAS-protocols_file-security_effective-permissions_{svm.uuid}_{path})"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="effective permission show")
        def effective_permission_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single EffectivePermission resource

            Args:
                file_permissions: Specifies the effective permission granted to a user on the specified file or folder path.
                path: Specifies the path of the file or the folder for which you want to display effective permissions. The path is relative to the SVM root volume. If \"-share-name\" is specified then path will be relative to the share path. 
                share_permissions: Specifies the effective permission granted to a user on the specified file or folder path.
                type: Specifies the user type. The following values are allowed: * windows  - Windows user * unix     - UNIX user 
                user: Specifies the user for which effective permission needs to be displayed for the specified path.
            """

            kwargs = {}
            if file_permissions is not None:
                kwargs["file_permissions"] = file_permissions
            if path is not None:
                kwargs["path"] = path
            if share_permissions is not None:
                kwargs["share_permissions"] = share_permissions
            if type is not None:
                kwargs["type"] = type
            if user is not None:
                kwargs["user"] = user
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = EffectivePermission(
                **kwargs
            )
            resource.get()
            return [resource]





