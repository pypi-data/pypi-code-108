r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
You can use this API to display local UNIX group information and to control UNIX group configurations.
## Retrieving UNIX group information
The UNIX group GET endpoint retrieves all of the local UNIX groups configurations for data SVMs.
## Examples
### Retrieving all of the fields for all of the UNIX group configurations
The UNIX group GET endpoint retrieves all of the local UNIX groups configurations for data SVMs.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UnixGroup

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(UnixGroup.get_collection(fields="*")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    UnixGroup(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/b009a9e7-4081-b576-7575-ada21efcaf16"
                    }
                },
                "uuid": "b009a9e7-4081-b576-7575-ada21efcaf16",
                "name": "vs1",
            },
            "id": 11,
            "users": [{"name": "user1"}, {"name": "user2"}, {"name": "user3"}],
            "name": "group1",
            "_links": {
                "self": {
                    "href": "/api/name-services/unix-groups/b009a9e7-4081-b576-7575-ada21efcaf16/group1"
                }
            },
        }
    ),
    UnixGroup(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/b009a9e7-4081-b576-7575-ada21efcaf16"
                    }
                },
                "uuid": "b009a9e7-4081-b576-7575-ada21efcaf16",
                "name": "vs1",
            },
            "id": 12,
            "users": [{"name": "user1"}, {"name": "user2"}],
            "name": "group2",
            "_links": {
                "self": {
                    "href": "/api/name-services/unix-groups/b009a9e7-4081-b576-7575-ada21efcaf16/group2"
                }
            },
        }
    ),
    UnixGroup(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/b009a9e7-4081-b576-7575-ada21efcad17"
                    }
                },
                "uuid": "b009a9e7-4081-b576-7575-ada21efcad17",
                "name": "vs2",
            },
            "id": 11,
            "users": [{"name": "user2"}, {"name": "user3"}],
            "name": "group1",
            "_links": {
                "self": {
                    "href": "/api/name-services/unix-groups/b009a9e7-4081-b576-7575-ada21efcad17/group1"
                }
            },
        }
    ),
]

```
</div>
</div>

### Retrieving all of the UNIX group configurations whose group name is 'group1'.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UnixGroup

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(UnixGroup.get_collection(name="group1")))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    UnixGroup(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/b009a9e7-4081-b576-7575-ada21efcaf16"
                    }
                },
                "uuid": "b009a9e7-4081-b576-7575-ada21efcaf16",
                "name": "vs1",
            },
            "id": 11,
            "name": "group1",
            "_links": {
                "self": {
                    "href": "/api/name-services/unix-groups/b009a9e7-4081-b576-7575-ada21efcaf16/group1"
                }
            },
        }
    )
]

```
</div>
</div>

## Creating a UNIX group configuration
The UNIX group POST endpoint creates a UNIX group configuration for the specified SVM.
## Example
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UnixGroup

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UnixGroup()
    resource.svm = {"uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"}
    resource.name = "group1"
    resource.id = 111
    resource.post(hydrate=True)
    print(resource)

```

## Updating a UNIX group configuration
The UNIX group PATCH endpoint updates the UNIX group ID of the specified UNIX group and the specified SVM.
## Example
### Modify the group ID of group1 to 112
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UnixGroup

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UnixGroup(
        name="group1", **{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"}
    )
    resource.id = 112
    resource.patch()

```

## Deleting a UNIX group configuration
The UNIX group DELETE endpoint deletes the specified UNIX group of the specified SVM.
## Example
### Delete the group 'group1'
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UnixGroup

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UnixGroup(
        name="group1", **{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"}
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


__all__ = ["UnixGroup", "UnixGroupSchema"]
__pdoc__ = {
    "UnixGroupSchema.resource": False,
    "UnixGroup.unix_group_show": False,
    "UnixGroup.unix_group_create": False,
    "UnixGroup.unix_group_modify": False,
    "UnixGroup.unix_group_delete": False,
}


class UnixGroupSchema(ResourceSchema):
    """The fields of the UnixGroup object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the unix_group. """

    id = Size(
        data_key="id",
    )
    r""" UNIX group ID of the specified user. """

    name = fields.Str(
        data_key="name",
    )
    r""" UNIX group name to be added to the local database. """

    skip_name_validation = fields.Boolean(
        data_key="skip_name_validation",
    )
    r""" Indicates whether or not the validation for the specified UNIX group name is disabled. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the unix_group. """

    users = fields.List(fields.Nested("netapp_ontap.models.unix_group_users_no_records.UnixGroupUsersNoRecordsSchema", unknown=EXCLUDE), data_key="users")
    r""" The users field of the unix_group. """

    @property
    def resource(self):
        return UnixGroup

    gettable_fields = [
        "links",
        "id",
        "name",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "users",
    ]
    """links,id,name,svm.links,svm.name,svm.uuid,users,"""

    patchable_fields = [
        "id",
        "name",
        "svm.name",
        "svm.uuid",
    ]
    """id,name,svm.name,svm.uuid,"""

    postable_fields = [
        "id",
        "name",
        "skip_name_validation",
        "svm.name",
        "svm.uuid",
    ]
    """id,name,skip_name_validation,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in UnixGroup.get_collection(fields=field)]
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
            raise NetAppRestError("UnixGroup modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class UnixGroup(Resource):
    """Allows interaction with UnixGroup objects on the host"""

    _schema = UnixGroupSchema
    _path = "/api/name-services/unix-groups"
    _keys = ["svm.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the UNIX groups for all of the SVMs. UNIX users who are the members of the group are also displayed.
### Related ONTAP commands
* `vserver services name-service unix-group show`
### Learn more
* [`DOC /name-services/unix-groups`](#docs-name-services-name-services_unix-groups)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="unix group show")
        def unix_group_show(
            fields: List[Choices.define(["id", "name", "skip_name_validation", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of UnixGroup resources

            Args:
                id: UNIX group ID of the specified user. 
                name: UNIX group name to be added to the local database. 
                skip_name_validation: Indicates whether or not the validation for the specified UNIX group name is disabled.
            """

            kwargs = {}
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if skip_name_validation is not None:
                kwargs["skip_name_validation"] = skip_name_validation
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return UnixGroup.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all UnixGroup resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["UnixGroup"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the UNIX group information of the specified group in the specified SVM.
### Learn more
* [`DOC /name-services/unix-groups`](#docs-name-services-name-services_unix-groups)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["UnixGroup"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["UnixGroup"], NetAppResponse]:
        r"""Creates the local UNIX group configuration for the specified SVM.<br/>
Group name and group ID are mandatory parameters.
### Learn more
* [`DOC /name-services/unix-groups`](#docs-name-services-name-services_unix-groups)
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
        records: Iterable["UnixGroup"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a UNIX group configuration for the specified SVM.
### Related ONTAP commands
* `vserver services name-service unix-group delete`
### Learn more
* [`DOC /name-services/unix-groups`](#docs-name-services-name-services_unix-groups)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the UNIX groups for all of the SVMs. UNIX users who are the members of the group are also displayed.
### Related ONTAP commands
* `vserver services name-service unix-group show`
### Learn more
* [`DOC /name-services/unix-groups`](#docs-name-services-name-services_unix-groups)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves UNIX group information for the specified group and SVM. UNIX users who are part of this group
are also retrieved.
### Related ONTAP commands
* `vserver services name-service unix-group show`
### Learn more
* [`DOC /name-services/unix-groups`](#docs-name-services-name-services_unix-groups)
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
        r"""Creates the local UNIX group configuration for the specified SVM.<br/>
Group name and group ID are mandatory parameters.
### Learn more
* [`DOC /name-services/unix-groups`](#docs-name-services-name-services_unix-groups)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="unix group create")
        async def unix_group_create(
        ) -> ResourceTable:
            """Create an instance of a UnixGroup resource

            Args:
                links: 
                id: UNIX group ID of the specified user. 
                name: UNIX group name to be added to the local database. 
                skip_name_validation: Indicates whether or not the validation for the specified UNIX group name is disabled.
                svm: 
                users: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if skip_name_validation is not None:
                kwargs["skip_name_validation"] = skip_name_validation
            if svm is not None:
                kwargs["svm"] = svm
            if users is not None:
                kwargs["users"] = users

            resource = UnixGroup(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create UnixGroup: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the UNIX group information of the specified group in the specified SVM.
### Learn more
* [`DOC /name-services/unix-groups`](#docs-name-services-name-services_unix-groups)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="unix group modify")
        async def unix_group_modify(
        ) -> ResourceTable:
            """Modify an instance of a UnixGroup resource

            Args:
                id: UNIX group ID of the specified user. 
                query_id: UNIX group ID of the specified user. 
                name: UNIX group name to be added to the local database. 
                query_name: UNIX group name to be added to the local database. 
                skip_name_validation: Indicates whether or not the validation for the specified UNIX group name is disabled.
                query_skip_name_validation: Indicates whether or not the validation for the specified UNIX group name is disabled.
            """

            kwargs = {}
            changes = {}
            if query_id is not None:
                kwargs["id"] = query_id
            if query_name is not None:
                kwargs["name"] = query_name
            if query_skip_name_validation is not None:
                kwargs["skip_name_validation"] = query_skip_name_validation

            if id is not None:
                changes["id"] = id
            if name is not None:
                changes["name"] = name
            if skip_name_validation is not None:
                changes["skip_name_validation"] = skip_name_validation

            if hasattr(UnixGroup, "find"):
                resource = UnixGroup.find(
                    **kwargs
                )
            else:
                resource = UnixGroup()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify UnixGroup: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a UNIX group configuration for the specified SVM.
### Related ONTAP commands
* `vserver services name-service unix-group delete`
### Learn more
* [`DOC /name-services/unix-groups`](#docs-name-services-name-services_unix-groups)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="unix group delete")
        async def unix_group_delete(
        ) -> None:
            """Delete an instance of a UnixGroup resource

            Args:
                id: UNIX group ID of the specified user. 
                name: UNIX group name to be added to the local database. 
                skip_name_validation: Indicates whether or not the validation for the specified UNIX group name is disabled.
            """

            kwargs = {}
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if skip_name_validation is not None:
                kwargs["skip_name_validation"] = skip_name_validation

            if hasattr(UnixGroup, "find"):
                resource = UnixGroup.find(
                    **kwargs
                )
            else:
                resource = UnixGroup()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete UnixGroup: %s" % err)


