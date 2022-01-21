r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
An IPspace is an addressing domain within which each IP address is unique. The same address may appear in a different IPspace, but the matching addresses are considered to be distinct. SVMs and broadcast domains, and therefore IP interfaces and Ethernet ports, are associated with a single IPspace. This endpoint supports the following operations: GET (collection and instance), POST, PATCH, and DELETE.
## Retrieving IPspace information
You can use the IPspaces GET API to retrieve all IPspaces configured in the cluster, including built-in and custom IPspaces, and specifically requested IPspaces.
## Examples
### Retrieving a list of the IPspaces in the cluster
The following example returns the requested list of IPspaces configured in the cluster.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Ipspace

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(Ipspace.get_collection(fields="*")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    Ipspace(
        {
            "name": "Default",
            "uuid": "dcc7e79c-5acc-11e8-b9de-005056b42b32",
            "_links": {
                "self": {
                    "href": "/api/network/ipspaces/dcc7e79c-5acc-11e8-b9de-005056b42b32"
                }
            },
        }
    ),
    Ipspace(
        {
            "name": "Cluster",
            "uuid": "dfd3c1b2-5acc-11e8-b9de-005056b42b32",
            "_links": {
                "self": {
                    "href": "/api/network/ipspaces/dfd3c1b2-5acc-11e8-b9de-005056b42b32"
                }
            },
        }
    ),
    Ipspace(
        {
            "name": "Ipspace1",
            "uuid": "dedec1be-5aec-1eee-beee-0eee56be2b3e",
            "_links": {
                "self": {
                    "href": "/api/network/ipspaces/dedec1be-5aec-1eee-beee-0eee56be2b3e"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving a specific IPspace in the cluster
The following example returns the specific IPspace requested. The system returns an error if there is no IPspace with the requested UUID.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Ipspace

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Ipspace(uuid="dfd3c1b2-5acc-11e8-b9de-005056b42b32")
    resource.get(fields="*")
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
Ipspace(
    {
        "name": "Default",
        "uuid": "dcc7e79c-5acc-11e8-b9de-005056b42b32",
        "_links": {
            "self": {
                "href": "/api/network/ipspaces/dcc7e79c-5acc-11e8-b9de-005056b42b32"
            }
        },
    }
)

```
</div>
</div>

---
## Creating IPspaces
You can use the network IPspaces POST API to create IPspaces.
<br/>
---
## Example
### Creating an IPspace
The following output displays the record returned after the creation of an IPspace with the name "ipspace1".
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Ipspace

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Ipspace()
    resource.name = "ipspace2"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
Ipspace(
    {
        "name": "ipspace2",
        "uuid": "4165655e-0528-11e9-bd68-005056bb046a",
        "_links": {
            "self": {
                "href": "/api/network/ipspaces/4165655e-0528-11e9-bd68-005056bb046a"
            }
        },
    }
)

```
</div>
</div>

---
## Updating IPspaces
You can use the IPspaces PATCH API to update the attributes of the IPspace.
<br/>
---
## Example
### Updating the name of an IPspace
The following PATCH request is used to update the name of the IPspace from "ipspace2" to "ipspace20".
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Ipspace

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Ipspace(uuid="4165655e-0528-11e9-bd68-005056bb046a")
    resource.name = "ipspace20"
    resource.patch()

```

---
## Deleting IPspaces
You can use the IPspaces DELETE API to delete an IPspace.
<br/>
---
## Example
### Deleting an IPspace
The following DELETE request is used to delete an IPspace.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Ipspace

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Ipspace(uuid="4165655e-0528-11e9-bd68-005056bb046a")
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


__all__ = ["Ipspace", "IpspaceSchema"]
__pdoc__ = {
    "IpspaceSchema.resource": False,
    "Ipspace.ipspace_show": False,
    "Ipspace.ipspace_create": False,
    "Ipspace.ipspace_modify": False,
    "Ipspace.ipspace_delete": False,
}


class IpspaceSchema(ResourceSchema):
    """The fields of the Ipspace object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the ipspace. """

    name = fields.Str(
        data_key="name",
    )
    r""" IPspace name

Example: ipspace1 """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The UUID that uniquely identifies the IPspace.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return Ipspace

    gettable_fields = [
        "links",
        "name",
        "uuid",
    ]
    """links,name,uuid,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Ipspace.get_collection(fields=field)]
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
            raise NetAppRestError("Ipspace modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Ipspace(Resource):
    """Allows interaction with Ipspace objects on the host"""

    _schema = IpspaceSchema
    _path = "/api/network/ipspaces"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of IPspaces for the entire cluster.
### Related ONTAP commands
* `network ipspace show`

### Learn more
* [`DOC /network/ipspaces`](#docs-networking-network_ipspaces)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ipspace show")
        def ipspace_show(
            fields: List[Choices.define(["name", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of Ipspace resources

            Args:
                name: IPspace name
                uuid: The UUID that uniquely identifies the IPspace.
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return Ipspace.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Ipspace resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["Ipspace"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an IPspace object.
### Related ONTAP commands
* `network ipspace rename`

### Learn more
* [`DOC /network/ipspaces`](#docs-networking-network_ipspaces)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["Ipspace"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["Ipspace"], NetAppResponse]:
        r"""Creates a new domain within which IP addresses are unique. SVMs, ports, and networks are scoped to a single IPspace.
### Required properties
* `name` - Name of the IPspace to create.
### Related ONTAP commands
* `network ipspace create`

### Learn more
* [`DOC /network/ipspaces`](#docs-networking-network_ipspaces)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["Ipspace"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an IPspace object.
### Related ONTAP commands
* `network ipspace delete`

### Learn more
* [`DOC /network/ipspaces`](#docs-networking-network_ipspaces)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of IPspaces for the entire cluster.
### Related ONTAP commands
* `network ipspace show`

### Learn more
* [`DOC /network/ipspaces`](#docs-networking-network_ipspaces)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves information about a specific IPspace.
### Related ONTAP commands
* `network ipspace show`

### Learn more
* [`DOC /network/ipspaces`](#docs-networking-network_ipspaces)"""
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
        r"""Creates a new domain within which IP addresses are unique. SVMs, ports, and networks are scoped to a single IPspace.
### Required properties
* `name` - Name of the IPspace to create.
### Related ONTAP commands
* `network ipspace create`

### Learn more
* [`DOC /network/ipspaces`](#docs-networking-network_ipspaces)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ipspace create")
        async def ipspace_create(
        ) -> ResourceTable:
            """Create an instance of a Ipspace resource

            Args:
                links: 
                name: IPspace name
                uuid: The UUID that uniquely identifies the IPspace.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if name is not None:
                kwargs["name"] = name
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = Ipspace(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create Ipspace: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an IPspace object.
### Related ONTAP commands
* `network ipspace rename`

### Learn more
* [`DOC /network/ipspaces`](#docs-networking-network_ipspaces)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ipspace modify")
        async def ipspace_modify(
        ) -> ResourceTable:
            """Modify an instance of a Ipspace resource

            Args:
                name: IPspace name
                query_name: IPspace name
                uuid: The UUID that uniquely identifies the IPspace.
                query_uuid: The UUID that uniquely identifies the IPspace.
            """

            kwargs = {}
            changes = {}
            if query_name is not None:
                kwargs["name"] = query_name
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if name is not None:
                changes["name"] = name
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(Ipspace, "find"):
                resource = Ipspace.find(
                    **kwargs
                )
            else:
                resource = Ipspace()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify Ipspace: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an IPspace object.
### Related ONTAP commands
* `network ipspace delete`

### Learn more
* [`DOC /network/ipspaces`](#docs-networking-network_ipspaces)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ipspace delete")
        async def ipspace_delete(
        ) -> None:
            """Delete an instance of a Ipspace resource

            Args:
                name: IPspace name
                uuid: The UUID that uniquely identifies the IPspace.
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(Ipspace, "find"):
                resource = Ipspace.find(
                    **kwargs
                )
            else:
                resource = Ipspace()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete Ipspace: %s" % err)


