r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
The CIFS server can use local groups for authorization when determining share, file and directory access rights.
You can use this API to display local group information and to control local group configurations.
## Retrieving local group information
The local group GET endpoint retrieves all of the local groups configurations for data SVMs.
## Examples
### Retrieving all of the fields for all of the local group configurations
The local group GET endpoint retrieves all of the local groups configurations for data SVMs.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsGroup

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(LocalCifsGroup.get_collection(fields="**")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    LocalCifsGroup(
        {
            "svm": {"uuid": "b009a9e7-4081-b576-7575-ada21efcaf16", "name": "vs1"},
            "members": [
                {"name": "CIFS_SERVER\\Administrator"},
                {"name": "AD_DOMAIN\\Domain Admins"},
            ],
            "sid": "S-1-5-32-544",
            "description": "Built-in Administrators group",
            "name": "BUILTIN\\Administrators",
        }
    ),
    LocalCifsGroup(
        {
            "svm": {"uuid": "b009a9e7-4081-b576-7575-ada21efcaf16", "name": "vs1"},
            "members": [{"name": "AD_DOMAIN\\Domain Users"}],
            "sid": "S-1-5-32-545",
            "description": "All users",
            "name": "BUILTIN\\Users",
        }
    ),
    LocalCifsGroup(
        {
            "svm": {"uuid": "b009a9e7-4081-b576-7575-ada21efcaf16", "name": "vs1"},
            "members": [{"name": "SACHILDAP02\\Domain Guests"}],
            "sid": "S-1-5-32-546",
            "description": "Built-in Guests Group",
            "name": "BUILTIN\\Guests",
        }
    ),
    LocalCifsGroup(
        {
            "svm": {"uuid": "b009a9e7-4081-b576-7575-ada21efcaf16", "name": "vs1"},
            "sid": "S-1-5-32-547",
            "description": "Restricted administrative privileges",
            "name": "BUILTIN\\Power Users",
        }
    ),
    LocalCifsGroup(
        {
            "svm": {"uuid": "b009a9e7-4081-b576-7575-ada21efcaf16", "name": "vs1"},
            "sid": "S-1-5-32-551",
            "description": "Backup Operators group",
            "name": "BUILTIN\\Backup Operators",
        }
    ),
    LocalCifsGroup(
        {
            "svm": {"uuid": "b009a9e7-4081-b576-7575-ada21efcaf16", "name": "vs1"},
            "sid": "S-1-5-21-256008430-3394229847-3930036330-1001",
            "description": "local group2",
            "name": "CIFS_SERVER\\group2",
        }
    ),
    LocalCifsGroup(
        {
            "svm": {"uuid": "5060077c-5be6-11eb-90b7-0050568e5169", "name": "vs2"},
            "members": [
                {"name": "VS2.CIFS\\Administrator"},
                {"name": "VS2.CIFS\\user3"},
                {"name": "SACHILDAP02\\Domain Admins"},
            ],
            "sid": "S-1-5-32-544",
            "description": "Built-in Administrators group",
            "name": "BUILTIN\\Administrators",
        }
    ),
    LocalCifsGroup(
        {
            "svm": {"uuid": "5060077c-5be6-11eb-90b7-0050568e5169", "name": "vs2"},
            "members": [{"name": "SACHILDAP02\\Domain Users"}],
            "sid": "S-1-5-32-545",
            "description": "All users",
            "name": "BUILTIN\\Users",
        }
    ),
    LocalCifsGroup(
        {
            "svm": {"uuid": "5060077c-5be6-11eb-90b7-0050568e5169", "name": "vs2"},
            "members": [{"name": "SACHILDAP02\\Domain Guests"}],
            "sid": "S-1-5-32-546",
            "description": "Built-in Guests Group",
            "name": "BUILTIN\\Guests",
        }
    ),
    LocalCifsGroup(
        {
            "svm": {"uuid": "5060077c-5be6-11eb-90b7-0050568e5169", "name": "vs2"},
            "sid": "S-1-5-32-547",
            "description": "Restricted administrative privileges",
            "name": "BUILTIN\\Power Users",
        }
    ),
    LocalCifsGroup(
        {
            "svm": {"uuid": "5060077c-5be6-11eb-90b7-0050568e5169", "name": "vs2"},
            "sid": "S-1-5-32-551",
            "description": "Backup Operators group",
            "name": "BUILTIN\\Backup Operators",
        }
    ),
    LocalCifsGroup(
        {
            "svm": {"uuid": "5060077c-5be6-11eb-90b7-0050568e5169", "name": "vs2"},
            "sid": "S-1-5-21-1625922807-3304708894-3529444428-1001",
            "description": "local group1",
            "name": "CIFS_SERVER\\group1",
        }
    ),
]

```
</div>
</div>

### Retrieving a local group configuration of a specific SVM and group
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsGroup

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsGroup(
        sid="S-1-5-21-256008430-3394229847-3930036330-1001",
        **{"svm.uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
LocalCifsGroup(
    {
        "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
        "sid": "S-1-5-21-256008430-3394229847-3930036330-1001",
        "description": "local group",
        "name": "CIFS_SERVER\\group1",
    }
)

```
</div>
</div>

## Creating a local group configuration
The local group POST endpoint creates a local group configuration for the specified SVM.
## Example
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsGroup

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsGroup()
    resource.svm = {"uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"}
    resource.name = "group1"
    resource.post(hydrate=True)
    print(resource)

```

## Updating a local group configuration
The local group PATCH endpoint updates the name and description of the specified local group and the specified SVM.
## Example
### Update the local group name from 'group1' to 'group2'
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsGroup

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsGroup(
        sid="S-1-5-21-256008430-3394229847-3930036330-1257",
        **{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"}
    )
    resource.name = "group2"
    resource.description = "local group"
    resource.patch()

```

## Deleting a local group configuration
The local group DELETE endpoint deletes the specified local group of the specified SVM.
## Example
### Delete the local group 'group1'
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsGroup

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsGroup(
        sid="S-1-5-21-256008430-3394229847-3930036330-1001",
        **{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"}
    )
    resource.delete()

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


__all__ = ["LocalCifsGroup", "LocalCifsGroupSchema"]
__pdoc__ = {
    "LocalCifsGroupSchema.resource": False,
    "LocalCifsGroup.local_cifs_group_show": False,
    "LocalCifsGroup.local_cifs_group_create": False,
    "LocalCifsGroup.local_cifs_group_modify": False,
    "LocalCifsGroup.local_cifs_group_delete": False,
}


class LocalCifsGroupSchema(ResourceSchema):
    """The fields of the LocalCifsGroup object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the local_cifs_group. """

    description = fields.Str(
        data_key="description",
        validate=len_validation(minimum=0, maximum=256),
    )
    r""" Description for the local group.


Example: This is a local group """

    members = fields.List(fields.Nested("netapp_ontap.models.local_cifs_group_members_no_records.LocalCifsGroupMembersNoRecordsSchema", unknown=EXCLUDE), data_key="members")
    r""" The members field of the local_cifs_group. """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=1),
    )
    r""" Local group name. The maximum supported length of a group name is 256 characters.


Example: SMB_SERVER01\group """

    sid = fields.Str(
        data_key="sid",
    )
    r""" The security ID of the local group which uniquely identifies the group. The group SID is automatically generated in POST and it is retrieved using the GET method.


Example: S-1-5-21-256008430-3394229847-3930036330-1001 """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the local_cifs_group. """

    @property
    def resource(self):
        return LocalCifsGroup

    gettable_fields = [
        "links",
        "description",
        "members",
        "name",
        "sid",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,description,members,name,sid,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "description",
        "name",
        "svm.name",
        "svm.uuid",
    ]
    """description,name,svm.name,svm.uuid,"""

    postable_fields = [
        "description",
        "name",
        "svm.name",
        "svm.uuid",
    ]
    """description,name,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in LocalCifsGroup.get_collection(fields=field)]
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
            raise NetAppRestError("LocalCifsGroup modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class LocalCifsGroup(Resource):
    """Allows interaction with LocalCifsGroup objects on the host"""

    _schema = LocalCifsGroupSchema
    _path = "/api/protocols/cifs/local-groups"
    _keys = ["svm.uuid", "sid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the local groups for all of the SVMs.
### Advanced properties
* `members`
### Related ONTAP commands
* `vserver cifs users-and-groups local-group show`
* `vserver cifs users-and-groups local-group show-members`
### Learn more
* [`DOC /protocols/cifs/local-groups`](#docs-NAS-protocols_cifs_local-groups)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local cifs group show")
        def local_cifs_group_show(
            fields: List[Choices.define(["description", "name", "sid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of LocalCifsGroup resources

            Args:
                description: Description for the local group. 
                name: Local group name. The maximum supported length of a group name is 256 characters. 
                sid: The security ID of the local group which uniquely identifies the group. The group SID is automatically generated in POST and it is retrieved using the GET method. 
            """

            kwargs = {}
            if description is not None:
                kwargs["description"] = description
            if name is not None:
                kwargs["name"] = name
            if sid is not None:
                kwargs["sid"] = sid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return LocalCifsGroup.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all LocalCifsGroup resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["LocalCifsGroup"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the local group information of the specified group in the specified SVM. This API can also be used to rename a local group.
### Related ONTAP commands
* `vserver cifs users-and-groups local-group modify`
* `vserver cifs users-and-groups local-group rename`
### Learn more
* [`DOC /protocols/cifs/local-groups`](#docs-NAS-protocols_cifs_local-groups)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["LocalCifsGroup"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["LocalCifsGroup"], NetAppResponse]:
        r"""Creates the local group configuration for the specified SVM.
### Important notes
* The group name can contain up to 256 characters.
* The group name cannot be terminated by a period.
* The group name does not support any of the following characters: \" / ? [ ] , : | < > + = ; ? * @ or ASCII characters in the range 1-31.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the local group.
* `name` - Name of the local group.
### Related ONTAP commands
* `vserver cifs users-and-groups local-group create`
### Learn more
* [`DOC /protocols/cifs/local-groups`](#docs-NAS-protocols_cifs_local-groups)
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
        records: Iterable["LocalCifsGroup"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a local group configuration for the specified SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups local-group delete`
### Learn more
* [`DOC /protocols/cifs/local-groups`](#docs-NAS-protocols_cifs_local-groups)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the local groups for all of the SVMs.
### Advanced properties
* `members`
### Related ONTAP commands
* `vserver cifs users-and-groups local-group show`
* `vserver cifs users-and-groups local-group show-members`
### Learn more
* [`DOC /protocols/cifs/local-groups`](#docs-NAS-protocols_cifs_local-groups)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves local group information for the specified group and SVM.
### Advanced properties
* `members`
### Related ONTAP commands
* `vserver cifs users-and-groups local-group show`
* `vserver cifs users-and-groups local-group show-members`
### Learn more
* [`DOC /protocols/cifs/local-groups`](#docs-NAS-protocols_cifs_local-groups)
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
        r"""Creates the local group configuration for the specified SVM.
### Important notes
* The group name can contain up to 256 characters.
* The group name cannot be terminated by a period.
* The group name does not support any of the following characters: \" / ? [ ] , : | < > + = ; ? * @ or ASCII characters in the range 1-31.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the local group.
* `name` - Name of the local group.
### Related ONTAP commands
* `vserver cifs users-and-groups local-group create`
### Learn more
* [`DOC /protocols/cifs/local-groups`](#docs-NAS-protocols_cifs_local-groups)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local cifs group create")
        async def local_cifs_group_create(
        ) -> ResourceTable:
            """Create an instance of a LocalCifsGroup resource

            Args:
                links: 
                description: Description for the local group. 
                members: 
                name: Local group name. The maximum supported length of a group name is 256 characters. 
                sid: The security ID of the local group which uniquely identifies the group. The group SID is automatically generated in POST and it is retrieved using the GET method. 
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if description is not None:
                kwargs["description"] = description
            if members is not None:
                kwargs["members"] = members
            if name is not None:
                kwargs["name"] = name
            if sid is not None:
                kwargs["sid"] = sid
            if svm is not None:
                kwargs["svm"] = svm

            resource = LocalCifsGroup(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create LocalCifsGroup: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the local group information of the specified group in the specified SVM. This API can also be used to rename a local group.
### Related ONTAP commands
* `vserver cifs users-and-groups local-group modify`
* `vserver cifs users-and-groups local-group rename`
### Learn more
* [`DOC /protocols/cifs/local-groups`](#docs-NAS-protocols_cifs_local-groups)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local cifs group modify")
        async def local_cifs_group_modify(
        ) -> ResourceTable:
            """Modify an instance of a LocalCifsGroup resource

            Args:
                description: Description for the local group. 
                query_description: Description for the local group. 
                name: Local group name. The maximum supported length of a group name is 256 characters. 
                query_name: Local group name. The maximum supported length of a group name is 256 characters. 
                sid: The security ID of the local group which uniquely identifies the group. The group SID is automatically generated in POST and it is retrieved using the GET method. 
                query_sid: The security ID of the local group which uniquely identifies the group. The group SID is automatically generated in POST and it is retrieved using the GET method. 
            """

            kwargs = {}
            changes = {}
            if query_description is not None:
                kwargs["description"] = query_description
            if query_name is not None:
                kwargs["name"] = query_name
            if query_sid is not None:
                kwargs["sid"] = query_sid

            if description is not None:
                changes["description"] = description
            if name is not None:
                changes["name"] = name
            if sid is not None:
                changes["sid"] = sid

            if hasattr(LocalCifsGroup, "find"):
                resource = LocalCifsGroup.find(
                    **kwargs
                )
            else:
                resource = LocalCifsGroup()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify LocalCifsGroup: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a local group configuration for the specified SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups local-group delete`
### Learn more
* [`DOC /protocols/cifs/local-groups`](#docs-NAS-protocols_cifs_local-groups)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local cifs group delete")
        async def local_cifs_group_delete(
        ) -> None:
            """Delete an instance of a LocalCifsGroup resource

            Args:
                description: Description for the local group. 
                name: Local group name. The maximum supported length of a group name is 256 characters. 
                sid: The security ID of the local group which uniquely identifies the group. The group SID is automatically generated in POST and it is retrieved using the GET method. 
            """

            kwargs = {}
            if description is not None:
                kwargs["description"] = description
            if name is not None:
                kwargs["name"] = name
            if sid is not None:
                kwargs["sid"] = sid

            if hasattr(LocalCifsGroup, "find"):
                resource = LocalCifsGroup.find(
                    **kwargs
                )
            else:
                resource = LocalCifsGroup()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete LocalCifsGroup: %s" % err)


