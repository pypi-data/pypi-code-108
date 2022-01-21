r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
You can use this API to display local UNIX user information and to control UNIX user configurations.
## Retrieving UNIX user information
You can use the UNIX user GET endpoint to retrieve all of the local UNIX user configurations for data SVMs.
## Examples
### Retrieving all of the fields for UNIX user configurations for all SVMs
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UnixUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(UnixUser.get_collection(fields="*")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    UnixUser(
        {
            "primary_gid": 0,
            "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
            "id": 7,
            "full_name": "string",
            "name": "string",
        }
    ),
    UnixUser(
        {
            "primary_gid": 65535,
            "svm": {"uuid": "3f479a01-2971-11eb-88e1-0050568eefd4", "name": "vs2"},
            "id": 65535,
            "full_name": "",
            "name": "nobody",
        }
    ),
    UnixUser(
        {
            "primary_gid": 65534,
            "svm": {"uuid": "3f479a01-2971-11eb-88e1-0050568eefd4", "name": "vs2"},
            "id": 65534,
            "full_name": "",
            "name": "pcuser",
        }
    ),
    UnixUser(
        {
            "primary_gid": 1,
            "svm": {"uuid": "3f479a01-2971-11eb-88e1-0050568eefd4", "name": "vs2"},
            "id": 0,
            "full_name": "",
            "name": "root",
        }
    ),
]

```
</div>
</div>

---
### Retrieving the UNIX user configuration of a specific SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UnixUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            UnixUser.get_collection(
                fields="*", **{"svm.uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
            )
        )
    )

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    UnixUser(
        {
            "primary_gid": 1,
            "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
            "id": 1,
            "full_name": "Full User Name for user1",
            "name": "user1",
        }
    )
]

```
</div>
</div>

---
### Retrieving a UNIX user configuration of a specific SVM and user
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UnixUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UnixUser(
        name="user1", **{"svm.uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
UnixUser(
    {
        "primary_gid": 1,
        "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
        "id": 1,
        "full_name": "Full User Name for user1",
        "name": "user1",
    }
)

```
</div>
</div>

---
## Creating a UNIX user configuration
The UNIX user POST endpoint creates a UNIX user configuration for the specified SVM.
## Examples
### Creating a UNIX user configuration with all fields specified
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UnixUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UnixUser()
    resource.full_name = "Full user name"
    resource.id = 7
    resource.name = "user2"
    resource.primary_gid = 10
    resource.skip_name_validation = False
    resource.svm = {"name": "vs1", "uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
    resource.post(hydrate=True)
    print(resource)

```

---
### Creating a UNIX user configuration with only mandatory fields specified
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UnixUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UnixUser()
    resource.id = 8
    resource.name = "user9"
    resource.primary_gid = 10
    resource.svm = {"name": "vs1", "uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
    resource.post(hydrate=True)
    print(resource)

```

---
## Updating a UNIX user configuration
The UNIX user PATCH endpoint updates the UNIX user configuration for the specified user and SVM. The following example shows a PATCH operation:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UnixUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UnixUser(
        name="user1", **{"svm.uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
    )
    resource.full_name = "Full name"
    resource.id = 7
    resource.primary_gid = 10
    resource.patch()

```

---
## Deleting a UNIX user configuration
The UNIX user DELETE endpoint deletes the specified UNIX user for the specified SVM. The following example shows a DELETE operation:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UnixUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UnixUser(
        name="user1", **{"svm.uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
    )
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


__all__ = ["UnixUser", "UnixUserSchema"]
__pdoc__ = {
    "UnixUserSchema.resource": False,
    "UnixUser.unix_user_show": False,
    "UnixUser.unix_user_create": False,
    "UnixUser.unix_user_modify": False,
    "UnixUser.unix_user_delete": False,
}


class UnixUserSchema(ResourceSchema):
    """The fields of the UnixUser object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the unix_user. """

    full_name = fields.Str(
        data_key="full_name",
    )
    r""" User's full name. """

    id = Size(
        data_key="id",
    )
    r""" UNIX user ID of the specified user. """

    name = fields.Str(
        data_key="name",
    )
    r""" UNIX user name to be added to the local database. """

    primary_gid = Size(
        data_key="primary_gid",
    )
    r""" Primary group ID to which the user belongs. """

    skip_name_validation = fields.Boolean(
        data_key="skip_name_validation",
    )
    r""" Indicates whether or not the validation for the specified UNIX user name is disabled. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the unix_user. """

    @property
    def resource(self):
        return UnixUser

    gettable_fields = [
        "links",
        "full_name",
        "id",
        "name",
        "primary_gid",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,full_name,id,name,primary_gid,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "full_name",
        "id",
        "primary_gid",
        "svm.name",
        "svm.uuid",
    ]
    """full_name,id,primary_gid,svm.name,svm.uuid,"""

    postable_fields = [
        "full_name",
        "id",
        "name",
        "primary_gid",
        "skip_name_validation",
        "svm.name",
        "svm.uuid",
    ]
    """full_name,id,name,primary_gid,skip_name_validation,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in UnixUser.get_collection(fields=field)]
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
            raise NetAppRestError("UnixUser modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class UnixUser(Resource):
    """Allows interaction with UnixUser objects on the host"""

    _schema = UnixUserSchema
    _path = "/api/name-services/unix-users"
    _keys = ["svm.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves all of the UNIX users for all of the SVMs.
### Related ONTAP commands
* `vserver services name-service unix-user show`

### Learn more
* [`DOC /name-services/unix-users`](#docs-name-services-name-services_unix-users)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="unix user show")
        def unix_user_show(
            fields: List[Choices.define(["full_name", "id", "name", "primary_gid", "skip_name_validation", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of UnixUser resources

            Args:
                full_name: User's full name. 
                id: UNIX user ID of the specified user. 
                name: UNIX user name to be added to the local database. 
                primary_gid: Primary group ID to which the user belongs. 
                skip_name_validation: Indicates whether or not the validation for the specified UNIX user name is disabled.
            """

            kwargs = {}
            if full_name is not None:
                kwargs["full_name"] = full_name
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if primary_gid is not None:
                kwargs["primary_gid"] = primary_gid
            if skip_name_validation is not None:
                kwargs["skip_name_validation"] = skip_name_validation
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return UnixUser.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all UnixUser resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["UnixUser"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates UNIX user information for the specified user and SVM.

### Learn more
* [`DOC /name-services/unix-users`](#docs-name-services-name-services_unix-users)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["UnixUser"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["UnixUser"], NetAppResponse]:
        r"""Creates the local UNIX user configuration for an SVM.<br/>

### Learn more
* [`DOC /name-services/unix-users`](#docs-name-services-name-services_unix-users)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["UnixUser"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a UNIX user configuration for the specified SVM.
### Related ONTAP commands
* `vserver services name-service unix-user delete`

### Learn more
* [`DOC /name-services/unix-users`](#docs-name-services-name-services_unix-users)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves all of the UNIX users for all of the SVMs.
### Related ONTAP commands
* `vserver services name-service unix-user show`

### Learn more
* [`DOC /name-services/unix-users`](#docs-name-services-name-services_unix-users)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves UNIX user information for the specified user and SVM.
### Related ONTAP commands
* `vserver services name-service unix-user show`

### Learn more
* [`DOC /name-services/unix-users`](#docs-name-services-name-services_unix-users)"""
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
        r"""Creates the local UNIX user configuration for an SVM.<br/>

### Learn more
* [`DOC /name-services/unix-users`](#docs-name-services-name-services_unix-users)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="unix user create")
        async def unix_user_create(
        ) -> ResourceTable:
            """Create an instance of a UnixUser resource

            Args:
                links: 
                full_name: User's full name. 
                id: UNIX user ID of the specified user. 
                name: UNIX user name to be added to the local database. 
                primary_gid: Primary group ID to which the user belongs. 
                skip_name_validation: Indicates whether or not the validation for the specified UNIX user name is disabled.
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if full_name is not None:
                kwargs["full_name"] = full_name
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if primary_gid is not None:
                kwargs["primary_gid"] = primary_gid
            if skip_name_validation is not None:
                kwargs["skip_name_validation"] = skip_name_validation
            if svm is not None:
                kwargs["svm"] = svm

            resource = UnixUser(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create UnixUser: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates UNIX user information for the specified user and SVM.

### Learn more
* [`DOC /name-services/unix-users`](#docs-name-services-name-services_unix-users)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="unix user modify")
        async def unix_user_modify(
        ) -> ResourceTable:
            """Modify an instance of a UnixUser resource

            Args:
                full_name: User's full name. 
                query_full_name: User's full name. 
                id: UNIX user ID of the specified user. 
                query_id: UNIX user ID of the specified user. 
                name: UNIX user name to be added to the local database. 
                query_name: UNIX user name to be added to the local database. 
                primary_gid: Primary group ID to which the user belongs. 
                query_primary_gid: Primary group ID to which the user belongs. 
                skip_name_validation: Indicates whether or not the validation for the specified UNIX user name is disabled.
                query_skip_name_validation: Indicates whether or not the validation for the specified UNIX user name is disabled.
            """

            kwargs = {}
            changes = {}
            if query_full_name is not None:
                kwargs["full_name"] = query_full_name
            if query_id is not None:
                kwargs["id"] = query_id
            if query_name is not None:
                kwargs["name"] = query_name
            if query_primary_gid is not None:
                kwargs["primary_gid"] = query_primary_gid
            if query_skip_name_validation is not None:
                kwargs["skip_name_validation"] = query_skip_name_validation

            if full_name is not None:
                changes["full_name"] = full_name
            if id is not None:
                changes["id"] = id
            if name is not None:
                changes["name"] = name
            if primary_gid is not None:
                changes["primary_gid"] = primary_gid
            if skip_name_validation is not None:
                changes["skip_name_validation"] = skip_name_validation

            if hasattr(UnixUser, "find"):
                resource = UnixUser.find(
                    **kwargs
                )
            else:
                resource = UnixUser()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify UnixUser: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a UNIX user configuration for the specified SVM.
### Related ONTAP commands
* `vserver services name-service unix-user delete`

### Learn more
* [`DOC /name-services/unix-users`](#docs-name-services-name-services_unix-users)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="unix user delete")
        async def unix_user_delete(
        ) -> None:
            """Delete an instance of a UnixUser resource

            Args:
                full_name: User's full name. 
                id: UNIX user ID of the specified user. 
                name: UNIX user name to be added to the local database. 
                primary_gid: Primary group ID to which the user belongs. 
                skip_name_validation: Indicates whether or not the validation for the specified UNIX user name is disabled.
            """

            kwargs = {}
            if full_name is not None:
                kwargs["full_name"] = full_name
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if primary_gid is not None:
                kwargs["primary_gid"] = primary_gid
            if skip_name_validation is not None:
                kwargs["skip_name_validation"] = skip_name_validation

            if hasattr(UnixUser, "find"):
                resource = UnixUser.find(
                    **kwargs
                )
            else:
                resource = UnixUser()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete UnixUser: %s" % err)


