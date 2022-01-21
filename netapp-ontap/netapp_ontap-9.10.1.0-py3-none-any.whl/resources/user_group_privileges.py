r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Privileges associated with local or Active Directory users or groups defines the permissions for the specified user or group. You can use this API to display and/or control privileges of local or Active Directory users or groups.
## Retrieving the privileges of a specific local or Active Directory user or group and an SVM
The users and groups privileges GET endpoint retrieves privileges of the specified local or Active Directory user or group and the SVM.
## Examples
### Retrieving the privileges of all of the users or groups of data SVMs.
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UserGroupPrivileges

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(UserGroupPrivileges.get_collection(fields="*")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    UserGroupPrivileges(
        {
            "privileges": ["SeChangeNotifyPrivilege", "SeTakeOwnershipPrivilege"],
            "name": "VS1.CIFS\\user1",
            "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
        }
    ),
    UserGroupPrivileges(
        {
            "privileges": ["SeBackupPrivilege", "SeTakeOwnershipPrivilege"],
            "name": "ACTIVE_DIRECTORY\\user",
            "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
        }
    ),
    UserGroupPrivileges(
        {
            "privileges": [
                "SeSecurityPrivilege",
                "SeBackupPrivilege",
                "SeRestorePrivilege",
            ],
            "name": "VS2.CIFS\\group1",
            "svm": {"uuid": "0ac79c37-3867-11eb-bece-0050568ed0a2", "name": "vs2"},
        }
    ),
]

```
</div>
</div>

### Retrieving the privileges of the specific SVM and user or group
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UserGroupPrivileges

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UserGroupPrivileges(
        name="user1", **{"svm.uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
UserGroupPrivileges(
    {
        "privileges": ["SeChangeNotifyPrivilege", "SeTakeOwnershipPrivilege"],
        "name": "VS1.CIFS\\user1",
        "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
    }
)

```
</div>
</div>

## Adding privileges to the local or Active Directory user or group
The users and groups privileges POST endpoint adds privileges to the specified local or Active Directory user or group and the SVM.
### Adding the privileges to the local user 'user1'
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UserGroupPrivileges

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UserGroupPrivileges()
    resource.privileges = [
        "SeSecurityPrivilege",
        "SeBackupPrivilege",
        "SeRestorePrivilege",
    ]
    resource.post(hydrate=True)
    print(resource)

```

## Updating the privileges of the local or Active Directory user or group of a specific SVM
## Example
### Updating the privileges of local user 'user1' in SVM 'vs1' to 'SeRestorePrivilege' and 'SeSecurityPrivilege'
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UserGroupPrivileges

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UserGroupPrivileges(
        name="user1", **{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"}
    )
    resource.privileges = ["SeRestorePrivilege", "SeSecurityPrivilege"]
    resource.patch()

```

### Reset all the privileges associated with the local user 'user1' in SVM 'vs1'
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UserGroupPrivileges

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UserGroupPrivileges(
        name="user1", **{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"}
    )
    resource.privileges = []
    resource.patch()

```

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


__all__ = ["UserGroupPrivileges", "UserGroupPrivilegesSchema"]
__pdoc__ = {
    "UserGroupPrivilegesSchema.resource": False,
    "UserGroupPrivileges.user_group_privileges_show": False,
    "UserGroupPrivileges.user_group_privileges_create": False,
    "UserGroupPrivileges.user_group_privileges_modify": False,
    "UserGroupPrivileges.user_group_privileges_delete": False,
}


class UserGroupPrivilegesSchema(ResourceSchema):
    """The fields of the UserGroupPrivileges object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the user_group_privileges. """

    name = fields.Str(
        data_key="name",
    )
    r""" Local or Active Directory user or group name.


Example: user1 """

    privileges = fields.List(fields.Str, data_key="privileges")
    r""" An array of privileges associated with the local or Active Directory user or group.
The available values are:

* SeTcbPrivilege              - Allows user to act as part of the operating system
* SeBackupPrivilege           - Allows user to back up files and directories, overriding any ACLs
* SeRestorePrivilege          - Allows user to restore files and directories, overriding any ACLs
* SeTakeOwnershipPrivilege    - Allows user to take ownership of files or other objects
* SeSecurityPrivilege         - Allows user to manage auditing and viewing/dumping/clearing the security log
* SeChangeNotifyPrivilege     - Allows user to bypass traverse checking """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the user_group_privileges. """

    @property
    def resource(self):
        return UserGroupPrivileges

    gettable_fields = [
        "links",
        "name",
        "privileges",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,name,privileges,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "privileges",
        "svm.name",
        "svm.uuid",
    ]
    """privileges,svm.name,svm.uuid,"""

    postable_fields = [
        "name",
        "privileges",
        "svm.name",
        "svm.uuid",
    ]
    """name,privileges,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in UserGroupPrivileges.get_collection(fields=field)]
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
            raise NetAppRestError("UserGroupPrivileges modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class UserGroupPrivileges(Resource):
    """Allows interaction with UserGroupPrivileges objects on the host"""

    _schema = UserGroupPrivilegesSchema
    _path = "/api/protocols/cifs/users-and-groups/privileges"
    _keys = ["svm.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves privileges of the specified local or Active Directory user or group and SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups privilege show`
### Learn more
* [`DOC /protocols/cifs/users-and-groups/privileges`](#docs-NAS-protocols_cifs_users-and-groups_privileges)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="user group privileges show")
        def user_group_privileges_show(
            fields: List[Choices.define(["name", "privileges", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of UserGroupPrivileges resources

            Args:
                name: Local or Active Directory user or group name. 
                privileges: An array of privileges associated with the local or Active Directory user or group. The available values are: * SeTcbPrivilege              - Allows user to act as part of the operating system * SeBackupPrivilege           - Allows user to back up files and directories, overriding any ACLs * SeRestorePrivilege          - Allows user to restore files and directories, overriding any ACLs * SeTakeOwnershipPrivilege    - Allows user to take ownership of files or other objects * SeSecurityPrivilege         - Allows user to manage auditing and viewing/dumping/clearing the security log * SeChangeNotifyPrivilege     - Allows user to bypass traverse checking 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if privileges is not None:
                kwargs["privileges"] = privileges
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return UserGroupPrivileges.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all UserGroupPrivileges resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["UserGroupPrivileges"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates privileges of the specified local or Active Directory user or group and SVM.
### Important note
* Specified privileges will replace all the existing privileges associated with the user or group.
* To reset privileges associated with the user or group, specify the privileges list as empty.
### Related ONTAP commands
* `vserver cifs users-and-groups privilege reset-privilege`
### Learn more
* [`DOC /protocols/cifs/users-and-groups/privileges`](#docs-NAS-protocols_cifs_users-and-groups_privileges)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["UserGroupPrivileges"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["UserGroupPrivileges"], NetAppResponse]:
        r"""Adds privileges to the specified local or Active Directory user or group and SVM.
### Important note
* Specified privileges are appended to the existing list of privileges.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM for which privileges are added to user or group.
* `name` - Exising local or Active Directory user or group for which privileges are to be added.
* `privileges` - List of privileges to be added to a user or group.
### Related ONTAP commands
* `vserver cifs users-and-groups privilege add-privilege`
### Learn more
* [`DOC /protocols/cifs/users-and-groups/privileges`](#docs-NAS-protocols_cifs_users-and-groups_privileges)
"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)


    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves privileges of the specified local or Active Directory user or group and SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups privilege show`
### Learn more
* [`DOC /protocols/cifs/users-and-groups/privileges`](#docs-NAS-protocols_cifs_users-and-groups_privileges)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves privileges of the specified local or Active Directory user or group and SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups privilege show`
### Learn more
* [`DOC /protocols/cifs/users-and-groups/privileges`](#docs-NAS-protocols_cifs_users-and-groups_privileges)
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
        r"""Adds privileges to the specified local or Active Directory user or group and SVM.
### Important note
* Specified privileges are appended to the existing list of privileges.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM for which privileges are added to user or group.
* `name` - Exising local or Active Directory user or group for which privileges are to be added.
* `privileges` - List of privileges to be added to a user or group.
### Related ONTAP commands
* `vserver cifs users-and-groups privilege add-privilege`
### Learn more
* [`DOC /protocols/cifs/users-and-groups/privileges`](#docs-NAS-protocols_cifs_users-and-groups_privileges)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="user group privileges create")
        async def user_group_privileges_create(
        ) -> ResourceTable:
            """Create an instance of a UserGroupPrivileges resource

            Args:
                links: 
                name: Local or Active Directory user or group name. 
                privileges: An array of privileges associated with the local or Active Directory user or group. The available values are: * SeTcbPrivilege              - Allows user to act as part of the operating system * SeBackupPrivilege           - Allows user to back up files and directories, overriding any ACLs * SeRestorePrivilege          - Allows user to restore files and directories, overriding any ACLs * SeTakeOwnershipPrivilege    - Allows user to take ownership of files or other objects * SeSecurityPrivilege         - Allows user to manage auditing and viewing/dumping/clearing the security log * SeChangeNotifyPrivilege     - Allows user to bypass traverse checking 
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if name is not None:
                kwargs["name"] = name
            if privileges is not None:
                kwargs["privileges"] = privileges
            if svm is not None:
                kwargs["svm"] = svm

            resource = UserGroupPrivileges(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create UserGroupPrivileges: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates privileges of the specified local or Active Directory user or group and SVM.
### Important note
* Specified privileges will replace all the existing privileges associated with the user or group.
* To reset privileges associated with the user or group, specify the privileges list as empty.
### Related ONTAP commands
* `vserver cifs users-and-groups privilege reset-privilege`
### Learn more
* [`DOC /protocols/cifs/users-and-groups/privileges`](#docs-NAS-protocols_cifs_users-and-groups_privileges)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="user group privileges modify")
        async def user_group_privileges_modify(
        ) -> ResourceTable:
            """Modify an instance of a UserGroupPrivileges resource

            Args:
                name: Local or Active Directory user or group name. 
                query_name: Local or Active Directory user or group name. 
                privileges: An array of privileges associated with the local or Active Directory user or group. The available values are: * SeTcbPrivilege              - Allows user to act as part of the operating system * SeBackupPrivilege           - Allows user to back up files and directories, overriding any ACLs * SeRestorePrivilege          - Allows user to restore files and directories, overriding any ACLs * SeTakeOwnershipPrivilege    - Allows user to take ownership of files or other objects * SeSecurityPrivilege         - Allows user to manage auditing and viewing/dumping/clearing the security log * SeChangeNotifyPrivilege     - Allows user to bypass traverse checking 
                query_privileges: An array of privileges associated with the local or Active Directory user or group. The available values are: * SeTcbPrivilege              - Allows user to act as part of the operating system * SeBackupPrivilege           - Allows user to back up files and directories, overriding any ACLs * SeRestorePrivilege          - Allows user to restore files and directories, overriding any ACLs * SeTakeOwnershipPrivilege    - Allows user to take ownership of files or other objects * SeSecurityPrivilege         - Allows user to manage auditing and viewing/dumping/clearing the security log * SeChangeNotifyPrivilege     - Allows user to bypass traverse checking 
            """

            kwargs = {}
            changes = {}
            if query_name is not None:
                kwargs["name"] = query_name
            if query_privileges is not None:
                kwargs["privileges"] = query_privileges

            if name is not None:
                changes["name"] = name
            if privileges is not None:
                changes["privileges"] = privileges

            if hasattr(UserGroupPrivileges, "find"):
                resource = UserGroupPrivileges.find(
                    **kwargs
                )
            else:
                resource = UserGroupPrivileges()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify UserGroupPrivileges: %s" % err)



