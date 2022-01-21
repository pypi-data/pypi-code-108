r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Access to files and folders can be secured over a network by configuring share access control lists (ACLs) on CIFS shares. Share-level ACLs can be configured by using either Windows users and groups or UNIX users and groups. A share-level ACL consists of a list of access control entries (ACEs). Each ACE contains a user or group name and a set of permissions that determines user or group access to the share, regardless of the security style of the volume or qtree containing the share. </br>
When an SMB user tries to access a share, ONTAP checks the share-level ACL to determine whether access should be granted. A share-level ACL only restricts access to files in the share; it never grants more access than the file level ACLs.
## Examples
### Creating a CIFS share ACL
To create a share ACL for a CIFS share, use the following API. Note the <i>return_records=true</i> query parameter used to obtain the newly created entry in the response.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsShareAcl

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = CifsShareAcl("sh1")
    resource.permission = "no_access"
    resource.type = "windows"
    resource.user_or_group = "root"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
CifsShareAcl(
    {
        "type": "windows",
        "permission": "no_access",
        "user_or_group": "root",
        "svm": {"name": "vs1"},
    }
)

```
</div>
</div>

---
### Retrieving all CIFS shares ACLs for a specific CIFS share for a specific SVM in the cluster
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsShareAcl

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(CifsShareAcl.get_collection("sh1", fields="*", return_timeout=15)))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    CifsShareAcl(
        {
            "type": "windows",
            "permission": "full_control",
            "user_or_group": "Everyone",
            "svm": {"uuid": "000c5cd2-ebdf-11e8-a96e-0050568ea3cb", "name": "vs1"},
        }
    ),
    CifsShareAcl(
        {
            "type": "windows",
            "permission": "no_access",
            "user_or_group": "root",
            "svm": {"uuid": "000c5cd2-ebdf-11e8-a96e-0050568ea3cb", "name": "vs1"},
        }
    ),
]

```
</div>
</div>

---
### Retrieving a CIFS share ACLs for a user or a group of type Windows or type UNIX on a CIFS share for a specific SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsShareAcl

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = CifsShareAcl("sh1", type="windows", user_or_group="everyone")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
CifsShareAcl(
    {
        "type": "windows",
        "permission": "full_control",
        "user_or_group": "everyone",
        "svm": {"uuid": "000c5cd2-ebdf-11e8-a96e-0050568ea3cb", "name": "vs1"},
    }
)

```
</div>
</div>

### Updating a CIFS share ACLs of a user or group on a CIFS share for a specific SVM
The CIFS share ACL being modified is identified by the UUID of its SVM, the CIFS share name, user or group name and the type of the user or group.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsShareAcl

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = CifsShareAcl("sh1", type="windows", user_or_group="everyone")
    resource.permission = "no_access"
    resource.patch()

```

### Removing a CIFS share ACLs of a user or group on a CIFS Share for a specific SVM
The CIFS share ACL being removed is identified by the UUID of its SVM, the CIFS share name, user or group name and the type of the user or group.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsShareAcl

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = CifsShareAcl("sh1", type="windows", user_or_group="everyone")
    resource.delete()

```

---
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


__all__ = ["CifsShareAcl", "CifsShareAclSchema"]
__pdoc__ = {
    "CifsShareAclSchema.resource": False,
    "CifsShareAcl.cifs_share_acl_show": False,
    "CifsShareAcl.cifs_share_acl_create": False,
    "CifsShareAcl.cifs_share_acl_modify": False,
    "CifsShareAcl.cifs_share_acl_delete": False,
}


class CifsShareAclSchema(ResourceSchema):
    """The fields of the CifsShareAcl object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the cifs_share_acl. """

    permission = fields.Str(
        data_key="permission",
        validate=enum_validation(['no_access', 'read', 'change', 'full_control']),
    )
    r""" Specifies the access rights that a user or group has on the defined CIFS Share.
The following values are allowed:

* no_access    - User does not have CIFS share access
* read         - User has only read access
* change       - User has change access
* full_control - User has full_control access


Valid choices:

* no_access
* read
* change
* full_control """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the cifs_share_acl. """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['windows', 'unix_user', 'unix_group']),
    )
    r""" Specifies the type of the user or group to add to the access control
list of a CIFS share. The following values are allowed:

* windows    - Windows user or group
* unix_user  - UNIX user
* unix_group - UNIX group


Valid choices:

* windows
* unix_user
* unix_group """

    user_or_group = fields.Str(
        data_key="user_or_group",
    )
    r""" Specifies the user or group name to add to the access control list of a CIFS share.

Example: ENGDOMAIN\ad_user """

    @property
    def resource(self):
        return CifsShareAcl

    gettable_fields = [
        "links",
        "permission",
        "share",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "type",
        "user_or_group",
    ]
    """links,permission,share,svm.links,svm.name,svm.uuid,type,user_or_group,"""

    patchable_fields = [
        "permission",
        "svm.name",
        "svm.uuid",
    ]
    """permission,svm.name,svm.uuid,"""

    postable_fields = [
        "permission",
        "svm.name",
        "svm.uuid",
        "type",
        "user_or_group",
    ]
    """permission,svm.name,svm.uuid,type,user_or_group,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in CifsShareAcl.get_collection(fields=field)]
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
            raise NetAppRestError("CifsShareAcl modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class CifsShareAcl(Resource):
    r""" The permissions that users and groups have on a CIFS share. """

    _schema = CifsShareAclSchema
    _path = "/api/protocols/cifs/shares/{svm[uuid]}/{cifs_share[share]}/acls"
    _keys = ["svm.uuid", "cifs_share.share", "user_or_group", "type"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the share-level ACL on a CIFS share.
### Related ONTAP commands
* `vserver cifs share access-control show`
### Learn more
* [`DOC /protocols/cifs/shares/{svm.uuid}/{share}/acls`](#docs-NAS-protocols_cifs_shares_{svm.uuid}_{share}_acls)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cifs share acl show")
        def cifs_share_acl_show(
            share,
            svm_uuid,
            permission: Choices.define(_get_field_list("permission"), cache_choices=True, inexact=True)=None,
            type: Choices.define(_get_field_list("type"), cache_choices=True, inexact=True)=None,
            user_or_group: Choices.define(_get_field_list("user_or_group"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["permission", "type", "user_or_group", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of CifsShareAcl resources

            Args:
                permission: Specifies the access rights that a user or group has on the defined CIFS Share. The following values are allowed: * no_access    - User does not have CIFS share access * read         - User has only read access * change       - User has change access * full_control - User has full_control access 
                type: Specifies the type of the user or group to add to the access control list of a CIFS share. The following values are allowed: * windows    - Windows user or group * unix_user  - UNIX user * unix_group - UNIX group 
                user_or_group: Specifies the user or group name to add to the access control list of a CIFS share.
            """

            kwargs = {}
            if permission is not None:
                kwargs["permission"] = permission
            if type is not None:
                kwargs["type"] = type
            if user_or_group is not None:
                kwargs["user_or_group"] = user_or_group
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return CifsShareAcl.get_collection(
                share,
                svm_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all CifsShareAcl resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["CifsShareAcl"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a share-level ACL on a CIFS share.
### Related ONTAP commands
* `vserver cifs share access-control modify`
### Learn more
* [`DOC /protocols/cifs/shares/{svm.uuid}/{share}/acls`](#docs-NAS-protocols_cifs_shares_{svm.uuid}_{share}_acls)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["CifsShareAcl"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["CifsShareAcl"], NetAppResponse]:
        r"""Creates a share-level ACL on a CIFS share.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the share acl.
* `share` - Existing CIFS share in which to create the share acl.
* `user_or_group` - Existing user or group name for which the acl is added on the CIFS share.
* `permission` - Access rights that a user or group has on the defined CIFS share.
### Default property values
* `type` - _windows_
### Related ONTAP commands
* `vserver cifs share access-control create`
### Learn more
* [`DOC /protocols/cifs/shares/{svm.uuid}/{share}/acls`](#docs-NAS-protocols_cifs_shares_{svm.uuid}_{share}_acls)
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
        records: Iterable["CifsShareAcl"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a share-level ACL on a CIFS share.
### Related ONTAP commands
* `vserver cifs share access-control delete`
### Learn more
* [`DOC /protocols/cifs/shares/{svm.uuid}/{share}/acls`](#docs-NAS-protocols_cifs_shares_{svm.uuid}_{share}_acls)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the share-level ACL on a CIFS share.
### Related ONTAP commands
* `vserver cifs share access-control show`
### Learn more
* [`DOC /protocols/cifs/shares/{svm.uuid}/{share}/acls`](#docs-NAS-protocols_cifs_shares_{svm.uuid}_{share}_acls)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the share-level ACL on CIFS share for a specified user or group.
### Related ONTAP commands
* `vserver cifs share access-control show`
### Learn more
* [`DOC /protocols/cifs/shares/{svm.uuid}/{share}/acls`](#docs-NAS-protocols_cifs_shares_{svm.uuid}_{share}_acls)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates a share-level ACL on a CIFS share.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the share acl.
* `share` - Existing CIFS share in which to create the share acl.
* `user_or_group` - Existing user or group name for which the acl is added on the CIFS share.
* `permission` - Access rights that a user or group has on the defined CIFS share.
### Default property values
* `type` - _windows_
### Related ONTAP commands
* `vserver cifs share access-control create`
### Learn more
* [`DOC /protocols/cifs/shares/{svm.uuid}/{share}/acls`](#docs-NAS-protocols_cifs_shares_{svm.uuid}_{share}_acls)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cifs share acl create")
        async def cifs_share_acl_create(
            share,
            svm_uuid,
            links: dict = None,
            permission: str = None,
            svm: dict = None,
            type: str = None,
            user_or_group: str = None,
        ) -> ResourceTable:
            """Create an instance of a CifsShareAcl resource

            Args:
                links: 
                permission: Specifies the access rights that a user or group has on the defined CIFS Share. The following values are allowed: * no_access    - User does not have CIFS share access * read         - User has only read access * change       - User has change access * full_control - User has full_control access 
                svm: 
                type: Specifies the type of the user or group to add to the access control list of a CIFS share. The following values are allowed: * windows    - Windows user or group * unix_user  - UNIX user * unix_group - UNIX group 
                user_or_group: Specifies the user or group name to add to the access control list of a CIFS share.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if permission is not None:
                kwargs["permission"] = permission
            if svm is not None:
                kwargs["svm"] = svm
            if type is not None:
                kwargs["type"] = type
            if user_or_group is not None:
                kwargs["user_or_group"] = user_or_group

            resource = CifsShareAcl(
                share,
                svm_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create CifsShareAcl: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a share-level ACL on a CIFS share.
### Related ONTAP commands
* `vserver cifs share access-control modify`
### Learn more
* [`DOC /protocols/cifs/shares/{svm.uuid}/{share}/acls`](#docs-NAS-protocols_cifs_shares_{svm.uuid}_{share}_acls)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cifs share acl modify")
        async def cifs_share_acl_modify(
            share,
            svm_uuid,
            permission: str = None,
            query_permission: str = None,
            type: str = None,
            query_type: str = None,
            user_or_group: str = None,
            query_user_or_group: str = None,
        ) -> ResourceTable:
            """Modify an instance of a CifsShareAcl resource

            Args:
                permission: Specifies the access rights that a user or group has on the defined CIFS Share. The following values are allowed: * no_access    - User does not have CIFS share access * read         - User has only read access * change       - User has change access * full_control - User has full_control access 
                query_permission: Specifies the access rights that a user or group has on the defined CIFS Share. The following values are allowed: * no_access    - User does not have CIFS share access * read         - User has only read access * change       - User has change access * full_control - User has full_control access 
                type: Specifies the type of the user or group to add to the access control list of a CIFS share. The following values are allowed: * windows    - Windows user or group * unix_user  - UNIX user * unix_group - UNIX group 
                query_type: Specifies the type of the user or group to add to the access control list of a CIFS share. The following values are allowed: * windows    - Windows user or group * unix_user  - UNIX user * unix_group - UNIX group 
                user_or_group: Specifies the user or group name to add to the access control list of a CIFS share.
                query_user_or_group: Specifies the user or group name to add to the access control list of a CIFS share.
            """

            kwargs = {}
            changes = {}
            if query_permission is not None:
                kwargs["permission"] = query_permission
            if query_type is not None:
                kwargs["type"] = query_type
            if query_user_or_group is not None:
                kwargs["user_or_group"] = query_user_or_group

            if permission is not None:
                changes["permission"] = permission
            if type is not None:
                changes["type"] = type
            if user_or_group is not None:
                changes["user_or_group"] = user_or_group

            if hasattr(CifsShareAcl, "find"):
                resource = CifsShareAcl.find(
                    share,
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = CifsShareAcl(share,svm_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify CifsShareAcl: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a share-level ACL on a CIFS share.
### Related ONTAP commands
* `vserver cifs share access-control delete`
### Learn more
* [`DOC /protocols/cifs/shares/{svm.uuid}/{share}/acls`](#docs-NAS-protocols_cifs_shares_{svm.uuid}_{share}_acls)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cifs share acl delete")
        async def cifs_share_acl_delete(
            share,
            svm_uuid,
            permission: str = None,
            type: str = None,
            user_or_group: str = None,
        ) -> None:
            """Delete an instance of a CifsShareAcl resource

            Args:
                permission: Specifies the access rights that a user or group has on the defined CIFS Share. The following values are allowed: * no_access    - User does not have CIFS share access * read         - User has only read access * change       - User has change access * full_control - User has full_control access 
                type: Specifies the type of the user or group to add to the access control list of a CIFS share. The following values are allowed: * windows    - Windows user or group * unix_user  - UNIX user * unix_group - UNIX group 
                user_or_group: Specifies the user or group name to add to the access control list of a CIFS share.
            """

            kwargs = {}
            if permission is not None:
                kwargs["permission"] = permission
            if type is not None:
                kwargs["type"] = type
            if user_or_group is not None:
                kwargs["user_or_group"] = user_or_group

            if hasattr(CifsShareAcl, "find"):
                resource = CifsShareAcl.find(
                    share,
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = CifsShareAcl(share,svm_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete CifsShareAcl: %s" % err)


