r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Displays and manages local mapping for hostnames.
## Retrieving all hosts table entries
The local-hosts GET endpoint to retrieve all hosts table entries.
## Examples
### Retrieving all the fields of all hosts table entries.
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(LocalHost.get_collection(return_timeout=15, fields="*")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    LocalHost(
        {
            "owner": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/6cdf045c-87ae-11eb-a56a-0050568e0287"
                    }
                },
                "uuid": "6cdf045c-87ae-11eb-a56a-0050568e0287",
                "name": "svm1",
            },
            "hostname": "host.sales.foo.com",
            "aliases": ["host1.sales.foo.com", "host2.sakes.foo.com"],
            "address": "1.1.1.1",
            "_links": {
                "self": {
                    "href": "/api/name-services/local-hosts/6cdf045c-87ae-11eb-a56a-0050568e0287/1.1.1.1"
                }
            },
        }
    ),
    LocalHost(
        {
            "owner": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/9d080552-7bff-11eb-a56a-0050568e0287"
                    }
                },
                "uuid": "9d080552-7bff-11eb-a56a-0050568e0287",
                "name": "svm2",
            },
            "hostname": "samplehost2",
            "address": "2.2.2.2",
            "_links": {
                "self": {
                    "href": "/api/name-services/local-hosts/9d080552-7bff-11eb-a56a-0050568e0287/2.2.2.2"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving the hosts table entry of a given svm and address(ipv4/ipv6).
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalHost(
        address="3.3.3.3", **{"owner.uuid": "9d080552-7bff-11eb-a56a-0050568e0287"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
LocalHost(
    {
        "owner": {
            "_links": {
                "self": {"href": "/api/svm/svms/9d080552-7bff-11eb-a56a-0050568e0287"}
            },
            "uuid": "9d080552-7bff-11eb-a56a-0050568e0287",
            "name": "svm1",
        },
        "hostname": "samplehost3",
        "aliases": ["host1.sales.foo.com", "host2.sakes.foo.com"],
        "address": "3.3.3.3",
        "_links": {
            "self": {
                "href": "/api/name-services/local-hosts/9d080552-7bff-11eb-a56a-0050568e0287/3.3.3.3"
            }
        },
    }
)

```
</div>
</div>

---
## Creating a hosts table entry
The local-hosts POST endpoint creates a new hosts table entry.
## Examples
### Creating a hosts table entry with all fields.
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalHost()
    resource.address = "3.3.3.3"
    resource.aliases = ["host1.sales.foo.com", "host2.sakes.foo.com"]
    resource.hostname = "samplehost3"
    resource.owner = {"name": "svm2", "uuid": "9d080552-7bff-11eb-a56a-0050568e0287"}
    resource.post(hydrate=True, return_records=False)
    print(resource)

```

---
### Creating a hosts table entry with only required fields.
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalHost()
    resource.address = "123.123.123.12"
    resource.hostname = "host.sales.foo.com"
    resource.owner = {"name": "svm2", "uuid": "9d080552-7bff-11eb-a56a-0050568e0287"}
    resource.post(hydrate=True, return_records=False)
    print(resource)

```

---
## Updating a hosts table entry
---
The local-hosts PATCH endpoint updates an existing hosts table entry.
## Example
### Updating aliases and hostname of a given svm and address(ipv4/ipv6).
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalHost(
        address="123.123.123.123",
        **{"owner.uuid": "9d080552-7bff-11eb-a56a-0050568e0287"}
    )
    resource.aliases = ["host1.sales.foo.com", "host2.sakes.foo.com"]
    resource.hostname = "host.sales.foo.com"
    resource.patch()

```

---
## Deleting a hosts table entry
---
The local-hosts DELETE endpoint deletes an existing hosts table entry.
## Example
### Deleting the hosts table entry of a given svm and address(ipv4/ipv6).
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalHost(
        address="1.1.1.1", **{"owner.uuid": "9d080552-7bff-11eb-a56a-0050568e0287"}
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


__all__ = ["LocalHost", "LocalHostSchema"]
__pdoc__ = {
    "LocalHostSchema.resource": False,
    "LocalHost.local_host_show": False,
    "LocalHost.local_host_create": False,
    "LocalHost.local_host_modify": False,
    "LocalHost.local_host_delete": False,
}


class LocalHostSchema(ResourceSchema):
    """The fields of the LocalHost object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the local_host. """

    address = fields.Str(
        data_key="address",
    )
    r""" IPv4/IPv6 address in dotted form.

Example: 123.123.123.123 """

    aliases = fields.List(fields.Str, data_key="aliases")
    r""" The list of aliases.

Example: ["host1.sales.foo.com","host2.sakes.foo.com"] """

    hostname = fields.Str(
        data_key="hostname",
        validate=len_validation(minimum=1, maximum=255),
    )
    r""" Canonical hostname.

Example: host.sales.foo.com """

    owner = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="owner", unknown=EXCLUDE)
    r""" The owner field of the local_host. """

    scope = fields.Str(
        data_key="scope",
        validate=enum_validation(['cluster', 'svm']),
    )
    r""" Scope of the entity. Set to "cluster" for cluster owned objects and to "svm" for SVM owned objects.

Valid choices:

* cluster
* svm """

    @property
    def resource(self):
        return LocalHost

    gettable_fields = [
        "links",
        "address",
        "aliases",
        "hostname",
        "owner.links",
        "owner.name",
        "owner.uuid",
        "scope",
    ]
    """links,address,aliases,hostname,owner.links,owner.name,owner.uuid,scope,"""

    patchable_fields = [
        "aliases",
        "hostname",
        "scope",
    ]
    """aliases,hostname,scope,"""

    postable_fields = [
        "address",
        "aliases",
        "hostname",
        "owner.name",
        "owner.uuid",
        "scope",
    ]
    """address,aliases,hostname,owner.name,owner.uuid,scope,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in LocalHost.get_collection(fields=field)]
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
            raise NetAppRestError("LocalHost modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class LocalHost(Resource):
    """Allows interaction with LocalHost objects on the host"""

    _schema = LocalHostSchema
    _path = "/api/name-services/local-hosts"
    _keys = ["owner.uuid", "address"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves all IP to hostname mappings for all SVMs of the cluster.
### Related ONTAP commands
* `vserver services name-service dns hosts show`
### Learn more
* [`DOC /name-services/local-hosts`](#docs-name-services-name-services_local-hosts)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local host show")
        def local_host_show(
            fields: List[Choices.define(["address", "aliases", "hostname", "scope", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of LocalHost resources

            Args:
                address: IPv4/IPv6 address in dotted form.
                aliases: The list of aliases.
                hostname: Canonical hostname.
                scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
            """

            kwargs = {}
            if address is not None:
                kwargs["address"] = address
            if aliases is not None:
                kwargs["aliases"] = aliases
            if hostname is not None:
                kwargs["hostname"] = hostname
            if scope is not None:
                kwargs["scope"] = scope
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return LocalHost.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all LocalHost resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["LocalHost"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""For a specified SVM and IP address, modifies the corresponding IP to hostname mapping.
### Related ONTAP commands
* `vserver services name-service dns hosts modify`
### Learn more
* [`DOC /name-services/local-hosts`](#docs-name-services-name-services_local-hosts)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["LocalHost"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["LocalHost"], NetAppResponse]:
        r"""Creates a new IP to hostname mapping.
### Required properties
* `owner.uuid` or `owner.name` - Existing SVM in which to create IP to host mapping.
* `address` - IPv4/IPv6 address in dotted form.
* `hostname` - Canonical hostname.
### Related ONTAP commands
* `vserver services name-service dns hosts create`
### Learn more
* [`DOC /name-services/local-hosts`](#docs-name-services-name-services_local-hosts)
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
        records: Iterable["LocalHost"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an existing host object.
### Related ONTAP commands
* `vserver services name-service dns hosts delete`
### Learn more
* [`DOC /name-services/local-hosts`](#docs-name-services-name-services_local-hosts)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves all IP to hostname mappings for all SVMs of the cluster.
### Related ONTAP commands
* `vserver services name-service dns hosts show`
### Learn more
* [`DOC /name-services/local-hosts`](#docs-name-services-name-services_local-hosts)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""For a specified SVM and IP address, returns the corresponding IP to hostname mapping.
### Related ONTAP commands
* `vserver services name-service dns hosts show`
### Learn more
* [`DOC /name-services/local-hosts`](#docs-name-services-name-services_local-hosts)
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
        r"""Creates a new IP to hostname mapping.
### Required properties
* `owner.uuid` or `owner.name` - Existing SVM in which to create IP to host mapping.
* `address` - IPv4/IPv6 address in dotted form.
* `hostname` - Canonical hostname.
### Related ONTAP commands
* `vserver services name-service dns hosts create`
### Learn more
* [`DOC /name-services/local-hosts`](#docs-name-services-name-services_local-hosts)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local host create")
        async def local_host_create(
        ) -> ResourceTable:
            """Create an instance of a LocalHost resource

            Args:
                links: 
                address: IPv4/IPv6 address in dotted form.
                aliases: The list of aliases.
                hostname: Canonical hostname.
                owner: 
                scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if address is not None:
                kwargs["address"] = address
            if aliases is not None:
                kwargs["aliases"] = aliases
            if hostname is not None:
                kwargs["hostname"] = hostname
            if owner is not None:
                kwargs["owner"] = owner
            if scope is not None:
                kwargs["scope"] = scope

            resource = LocalHost(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create LocalHost: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""For a specified SVM and IP address, modifies the corresponding IP to hostname mapping.
### Related ONTAP commands
* `vserver services name-service dns hosts modify`
### Learn more
* [`DOC /name-services/local-hosts`](#docs-name-services-name-services_local-hosts)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local host modify")
        async def local_host_modify(
        ) -> ResourceTable:
            """Modify an instance of a LocalHost resource

            Args:
                address: IPv4/IPv6 address in dotted form.
                query_address: IPv4/IPv6 address in dotted form.
                aliases: The list of aliases.
                query_aliases: The list of aliases.
                hostname: Canonical hostname.
                query_hostname: Canonical hostname.
                scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
                query_scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
            """

            kwargs = {}
            changes = {}
            if query_address is not None:
                kwargs["address"] = query_address
            if query_aliases is not None:
                kwargs["aliases"] = query_aliases
            if query_hostname is not None:
                kwargs["hostname"] = query_hostname
            if query_scope is not None:
                kwargs["scope"] = query_scope

            if address is not None:
                changes["address"] = address
            if aliases is not None:
                changes["aliases"] = aliases
            if hostname is not None:
                changes["hostname"] = hostname
            if scope is not None:
                changes["scope"] = scope

            if hasattr(LocalHost, "find"):
                resource = LocalHost.find(
                    **kwargs
                )
            else:
                resource = LocalHost()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify LocalHost: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an existing host object.
### Related ONTAP commands
* `vserver services name-service dns hosts delete`
### Learn more
* [`DOC /name-services/local-hosts`](#docs-name-services-name-services_local-hosts)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local host delete")
        async def local_host_delete(
        ) -> None:
            """Delete an instance of a LocalHost resource

            Args:
                address: IPv4/IPv6 address in dotted form.
                aliases: The list of aliases.
                hostname: Canonical hostname.
                scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
            """

            kwargs = {}
            if address is not None:
                kwargs["address"] = address
            if aliases is not None:
                kwargs["aliases"] = aliases
            if hostname is not None:
                kwargs["hostname"] = hostname
            if scope is not None:
                kwargs["scope"] = scope

            if hasattr(LocalHost, "find"):
                resource = LocalHost.find(
                    **kwargs
                )
            else:
                resource = LocalHost()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete LocalHost: %s" % err)


