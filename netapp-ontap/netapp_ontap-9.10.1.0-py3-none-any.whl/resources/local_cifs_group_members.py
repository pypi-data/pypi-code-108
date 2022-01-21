r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
You can use this API to display local group members and to add or delete local users, Active Directory users and/or Active Directory groups to a local group of an SVM.
## Examples
### Retrieving the members of a specific local group
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsGroupMembers

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            LocalCifsGroupMembers.get_collection(
                "S-1-5-21-256008430-3394229847-3930036330-1257"
            )
        )
    )

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    LocalCifsGroupMembers({"name": "CIFS_SERVER1\\user1"}),
    LocalCifsGroupMembers({"name": "CIFS_SERVER1\\user2"}),
]

```
</div>
</div>

## Adding members to a local group
The local group members POST endpoint adds local users, Active Directory users and/or Active Directory groups to the specified local group and the SVM.
### Adding local users to a group
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsGroupMembers

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsGroupMembers("S-1-5-21-256008430-3394229847-3930036330-1001")
    resource.records = [{"name": "user1"}, {"name": "user2"}]
    resource.post(hydrate=True)
    print(resource)

```

## Deleting local users from the local group of a specific SVM
## Example
### Delete the local users 'user1' and 'user2' from the specified local group
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsGroupMembers

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsGroupMembers("S-1-5-21-256008430-3394229847-3930036330-1001")
    resource.delete(body={"records": [{"name": "user1"}, {"name": "user2"}]})

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


__all__ = ["LocalCifsGroupMembers", "LocalCifsGroupMembersSchema"]
__pdoc__ = {
    "LocalCifsGroupMembersSchema.resource": False,
    "LocalCifsGroupMembers.local_cifs_group_members_show": False,
    "LocalCifsGroupMembers.local_cifs_group_members_create": False,
    "LocalCifsGroupMembers.local_cifs_group_members_modify": False,
    "LocalCifsGroupMembers.local_cifs_group_members_delete": False,
}


class LocalCifsGroupMembersSchema(ResourceSchema):
    """The fields of the LocalCifsGroupMembers object"""

    name = fields.Str(
        data_key="name",
    )
    r""" Local user, Active Directory user, or Active Directory group which is a member of the specified local group. """

    records = fields.List(fields.Nested("netapp_ontap.models.local_cifs_group_members_no_records.LocalCifsGroupMembersNoRecordsSchema", unknown=EXCLUDE), data_key="records")
    r""" An array of local users, Active Directory users, and Active Directory groups specified to add or delete multiple members to or from a local group in a single API call.
Not allowed when the `name` property is used. """

    @property
    def resource(self):
        return LocalCifsGroupMembers

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
        "records",
    ]
    """records,"""

    postable_fields = [
        "name",
        "records",
    ]
    """name,records,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in LocalCifsGroupMembers.get_collection(fields=field)]
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
            raise NetAppRestError("LocalCifsGroupMembers modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class LocalCifsGroupMembers(Resource):
    """Allows interaction with LocalCifsGroupMembers objects on the host"""

    _schema = LocalCifsGroupMembersSchema
    _path = "/api/protocols/cifs/local-groups/{svm[uuid]}/{local_cifs_group[sid]}/members"
    _keys = ["svm.uuid", "local_cifs_group.sid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves local users, Active Directory users and Active Directory groups which are members of the specified local group and SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups local-group show-members`
### Learn more
* [`DOC /protocols/cifs/local-groups/{svm.uuid}/{local_cifs_group.sid}/members`](#docs-NAS-protocols_cifs_local-groups_{svm.uuid}_{local_cifs_group.sid}_members)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local cifs group members show")
        def local_cifs_group_members_show(
            local_cifs_group_sid,
            svm_uuid,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["name", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of LocalCifsGroupMembers resources

            Args:
                name: Local user, Active Directory user, or Active Directory group which is a member of the specified local group. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return LocalCifsGroupMembers.get_collection(
                local_cifs_group_sid,
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
        """Returns a count of all LocalCifsGroupMembers resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["LocalCifsGroupMembers"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["LocalCifsGroupMembers"], NetAppResponse]:
        r"""Adds local users, Active Directory users and Active Directory groups to the specified local group and SVM.
### Important note
* Specified members are appended to the existing list of members.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM for which members are added to local group.
* `local_cifs_group.sid` -  Security ID of the local group to which members are added.
* `name` or `records` - Local users, Active Directory users, or Active Directory groups to be added to a particular local group.
### Related ONTAP commands
* `vserver cifs users-and-groups local-group add-members`
### Learn more
* [`DOC /protocols/cifs/local-groups/{svm.uuid}/{local_cifs_group.sid}/members`](#docs-NAS-protocols_cifs_local-groups_{svm.uuid}_{local_cifs_group.sid}_members)
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
        records: Iterable["LocalCifsGroupMembers"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the local user, Active Directory user and/or Active Directory group from the specified local group and SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups local-group remove-members`
### Learn more
* [`DOC /protocols/cifs/local-groups/{svm.uuid}/{local_cifs_group.sid}/members`](#docs-NAS-protocols_cifs_local-groups_{svm.uuid}_{local_cifs_group.sid}_members)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves local users, Active Directory users and Active Directory groups which are members of the specified local group and SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups local-group show-members`
### Learn more
* [`DOC /protocols/cifs/local-groups/{svm.uuid}/{local_cifs_group.sid}/members`](#docs-NAS-protocols_cifs_local-groups_{svm.uuid}_{local_cifs_group.sid}_members)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves local user, Active Directory user and Active Directory group which is member of the specified local group and SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups local-group show-members`
### Learn more
* [`DOC /protocols/cifs/local-groups/{svm.uuid}/{local_cifs_group.sid}/members`](#docs-NAS-protocols_cifs_local-groups_{svm.uuid}_{local_cifs_group.sid}_members)
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
        r"""Adds local users, Active Directory users and Active Directory groups to the specified local group and SVM.
### Important note
* Specified members are appended to the existing list of members.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM for which members are added to local group.
* `local_cifs_group.sid` -  Security ID of the local group to which members are added.
* `name` or `records` - Local users, Active Directory users, or Active Directory groups to be added to a particular local group.
### Related ONTAP commands
* `vserver cifs users-and-groups local-group add-members`
### Learn more
* [`DOC /protocols/cifs/local-groups/{svm.uuid}/{local_cifs_group.sid}/members`](#docs-NAS-protocols_cifs_local-groups_{svm.uuid}_{local_cifs_group.sid}_members)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local cifs group members create")
        async def local_cifs_group_members_create(
            local_cifs_group_sid,
            svm_uuid,
            name: str = None,
            records: dict = None,
        ) -> ResourceTable:
            """Create an instance of a LocalCifsGroupMembers resource

            Args:
                name: Local user, Active Directory user, or Active Directory group which is a member of the specified local group. 
                records: An array of local users, Active Directory users, and Active Directory groups specified to add or delete multiple members to or from a local group in a single API call. Not allowed when the `name` property is used. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if records is not None:
                kwargs["records"] = records

            resource = LocalCifsGroupMembers(
                local_cifs_group_sid,
                svm_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create LocalCifsGroupMembers: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the local user, Active Directory user and/or Active Directory group from the specified local group and SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups local-group remove-members`
### Learn more
* [`DOC /protocols/cifs/local-groups/{svm.uuid}/{local_cifs_group.sid}/members`](#docs-NAS-protocols_cifs_local-groups_{svm.uuid}_{local_cifs_group.sid}_members)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local cifs group members delete")
        async def local_cifs_group_members_delete(
            local_cifs_group_sid,
            svm_uuid,
            name: str = None,
        ) -> None:
            """Delete an instance of a LocalCifsGroupMembers resource

            Args:
                name: Local user, Active Directory user, or Active Directory group which is a member of the specified local group. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name

            if hasattr(LocalCifsGroupMembers, "find"):
                resource = LocalCifsGroupMembers.find(
                    local_cifs_group_sid,
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = LocalCifsGroupMembers(local_cifs_group_sid,svm_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete LocalCifsGroupMembers: %s" % err)


