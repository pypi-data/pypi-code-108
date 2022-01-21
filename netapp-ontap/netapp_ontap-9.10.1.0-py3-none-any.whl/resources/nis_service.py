r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
NIS servers are used to authenticate user and client computers. NIS domain name and NIS server information is required to configure NIS.
It is important to note that this API is used to retrieve and manage NIS server configurations for data SVMs only. NIS configuration for the cluster is managed via [`/api/security/authentication/cluster/nis`](#docs-security-security_authentication_cluster_nis).
## Retrieving NIS Information
The NIS GET endpoint retrieves all of the NIS configurations for data SVMs.
## Examples
### Retrieving all fields for all NIS configurations
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NisService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(NisService.get_collection(fields="*")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    NisService(
        {
            "domain": "domainA.example.com",
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/179d3c85-7053-11e8-b9b8-005056b41bd1"
                    }
                },
                "uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1",
                "name": "vs1",
            },
            "servers": ["10.10.10.10", "example.com"],
            "_links": {
                "self": {
                    "href": "/api/name-services/nis/179d3c85-7053-11e8-b9b8-005056b41bd1"
                }
            },
        }
    ),
    NisService(
        {
            "domain": "domainB.example.com",
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/6a52023b-7066-11e8-b9b8-005056b41bd1"
                    }
                },
                "uuid": "6a52023b-7066-11e8-b9b8-005056b41bd1",
                "name": "vs2",
            },
            "servers": ["2.2.2.2", "3.3.3.3", "4.4.4.4"],
            "_links": {
                "self": {
                    "href": "/api/name-services/nis/6a52023b-7066-11e8-b9b8-005056b41bd1"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving all NIS configurations whose bound servers start with *10*
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NisService

with HostConnection("<mgmt-ip", username="admin", password="password", verify=False):
    print(list(NisService.get_collection(bound_servers="10*")))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    NisService(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/179d3c85-7053-11e8-b9b8-005056b41bd1"
                    }
                },
                "uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1",
                "name": "vs1",
            },
            "_links": {
                "self": {
                    "href": "/api/name-services/nis/6a52023b-7066-11e8-b9b8-005056b41bd1"
                }
            },
        }
    )
]

```
</div>
</div>

---
### Retrieving the NIS configuration of a specific SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NisService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NisService(**{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"})
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
NisService(
    {
        "bound_servers": ["10.10.10.10"],
        "domain": "domainA.example.com",
        "svm": {"uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1", "name": "vs1"},
        "servers": ["10.10.10.10", "example.com"],
    }
)

```
</div>
</div>

---
## Creating a NIS configuration
The NIS POST endpoint creates a NIS configuration for the specified SVM.
## Example
The following example shows a POST operation:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NisService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NisService()
    resource.svm = {"uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"}
    resource.domain = "domainA.example.com"
    resource.servers = ["10.10.10.10", "example.com"]
    resource.post(hydrate=True)
    print(resource)

```

---
## Updating the NIS configuration
The NIS PATCH endpoint updates the NIS configuration for the specified NIS server.
## Examples
### Updating the domain
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NisService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NisService(**{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"})
    resource.domain = "domainC.example.com"
    resource.servers = ["13.13.13.13"]
    resource.patch()

```

---
### Updating the server
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NisService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NisService(**{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"})
    resource.servers = ["14.14.14.14"]
    resource.patch()

```

---
## Deleting a NIS configuration
The NIS DELETE endpoint deletes the NIS configuration for the specified SVM.
## Example
The following example shows a DELETE operation:
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NisService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NisService(**{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"})
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


__all__ = ["NisService", "NisServiceSchema"]
__pdoc__ = {
    "NisServiceSchema.resource": False,
    "NisService.nis_service_show": False,
    "NisService.nis_service_create": False,
    "NisService.nis_service_modify": False,
    "NisService.nis_service_delete": False,
}


class NisServiceSchema(ResourceSchema):
    """The fields of the NisService object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the nis_service. """

    bound_servers = fields.List(fields.Str, data_key="bound_servers")
    r""" The bound_servers field of the nis_service. """

    domain = fields.Str(
        data_key="domain",
        validate=len_validation(minimum=1, maximum=64),
    )
    r""" The NIS domain to which this configuration belongs. """

    servers = fields.List(fields.Str, data_key="servers")
    r""" A list of hostnames or IP addresses of NIS servers used
by the NIS domain configuration. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the nis_service. """

    @property
    def resource(self):
        return NisService

    gettable_fields = [
        "links",
        "bound_servers",
        "domain",
        "servers",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,bound_servers,domain,servers,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "domain",
        "servers",
        "svm.name",
        "svm.uuid",
    ]
    """domain,servers,svm.name,svm.uuid,"""

    postable_fields = [
        "domain",
        "servers",
        "svm.name",
        "svm.uuid",
    ]
    """domain,servers,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NisService.get_collection(fields=field)]
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
            raise NetAppRestError("NisService modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NisService(Resource):
    """Allows interaction with NisService objects on the host"""

    _schema = NisServiceSchema
    _path = "/api/name-services/nis"
    _keys = ["svm.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves NIS domain configurations of all the SVMs. The bound_servers field indicates the successfully bound NIS servers. Lookups and authentications fail if there are no bound servers.
### Related ONTAP commands
* `vserver services name-service nis-domain show`
* `vserver services name-service nis-domain show-bound`
### Learn more
* [`DOC /name-services/nis`](#docs-name-services-name-services_nis)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nis service show")
        def nis_service_show(
            fields: List[Choices.define(["bound_servers", "domain", "servers", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of NisService resources

            Args:
                bound_servers: 
                domain: The NIS domain to which this configuration belongs. 
                servers: A list of hostnames or IP addresses of NIS servers used by the NIS domain configuration. 
            """

            kwargs = {}
            if bound_servers is not None:
                kwargs["bound_servers"] = bound_servers
            if domain is not None:
                kwargs["domain"] = domain
            if servers is not None:
                kwargs["servers"] = servers
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return NisService.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NisService resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["NisService"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates NIS domain and server configuration of an SVM.<br/>
### Important notes
  - Both NIS domain and servers can be modified.
  - Domains and servers cannot be empty.
  - Both FQDNs and IP addresses are supported for the servers field.
  - If the domain is modified, NIS servers must also be specified.
  - IPv6 must be enabled if IPv6 family addresses are specified for the servers field.
### Related ONTAP commands
* `vserver services name-service nis-domain modify`
### Learn more
* [`DOC /name-services/nis`](#docs-name-services-name-services_nis)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["NisService"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["NisService"], NetAppResponse]:
        r"""Creates an NIS domain and server confguration for a data SVM.
NIS configuration for the cluster is managed via [`/api/security/authentication/cluster/nis`](#docs-security-security_authentication_cluster_nis).<br/>
### Important notes
  - Each SVM can have one NIS domain configuration.
  - Multiple SVMs can be configured with the same NIS domain. Specify the NIS domain and NIS servers as input.Domain name and servers fields cannot be empty.
  - Both FQDNs and IP addresses are supported for the servers field.
  - IPv6 must be enabled if IPv6 family addresses are specified in the servers field.
  - A maximum of ten NIS servers are supported.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the NIS configuration.
* `domain` - NIS domain to which the configuration belongs.
* `servers` - List of NIS server IP addresses.
### Related ONTAP commands
* `vserver services name-service nis-domain create`
### Learn more
* [`DOC /name-services/nis`](#docs-name-services-name-services_nis)
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
        records: Iterable["NisService"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the NIS domain configuration of an SVM. NIS can be removed as a source from ns-switch if NIS is not used for lookups.
### Related ONTAP commands
* `vserver services name-service nis-domain delete`
### Learn more
* [`DOC /name-services/nis`](#docs-name-services-name-services_nis)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves NIS domain configurations of all the SVMs. The bound_servers field indicates the successfully bound NIS servers. Lookups and authentications fail if there are no bound servers.
### Related ONTAP commands
* `vserver services name-service nis-domain show`
* `vserver services name-service nis-domain show-bound`
### Learn more
* [`DOC /name-services/nis`](#docs-name-services-name-services_nis)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves NIS domain and server configurations of an SVM. Both NIS domain and servers are displayed by default. The bound_servers field indicates the successfully bound NIS servers.
### Related ONTAP commands
* `vserver services name-service nis-domain show`
* `vserver services name-service nis-domain show-bound`
### Learn more
* [`DOC /name-services/nis`](#docs-name-services-name-services_nis)
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
        r"""Creates an NIS domain and server confguration for a data SVM.
NIS configuration for the cluster is managed via [`/api/security/authentication/cluster/nis`](#docs-security-security_authentication_cluster_nis).<br/>
### Important notes
  - Each SVM can have one NIS domain configuration.
  - Multiple SVMs can be configured with the same NIS domain. Specify the NIS domain and NIS servers as input.Domain name and servers fields cannot be empty.
  - Both FQDNs and IP addresses are supported for the servers field.
  - IPv6 must be enabled if IPv6 family addresses are specified in the servers field.
  - A maximum of ten NIS servers are supported.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the NIS configuration.
* `domain` - NIS domain to which the configuration belongs.
* `servers` - List of NIS server IP addresses.
### Related ONTAP commands
* `vserver services name-service nis-domain create`
### Learn more
* [`DOC /name-services/nis`](#docs-name-services-name-services_nis)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nis service create")
        async def nis_service_create(
        ) -> ResourceTable:
            """Create an instance of a NisService resource

            Args:
                links: 
                bound_servers: 
                domain: The NIS domain to which this configuration belongs. 
                servers: A list of hostnames or IP addresses of NIS servers used by the NIS domain configuration. 
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if bound_servers is not None:
                kwargs["bound_servers"] = bound_servers
            if domain is not None:
                kwargs["domain"] = domain
            if servers is not None:
                kwargs["servers"] = servers
            if svm is not None:
                kwargs["svm"] = svm

            resource = NisService(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create NisService: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates NIS domain and server configuration of an SVM.<br/>
### Important notes
  - Both NIS domain and servers can be modified.
  - Domains and servers cannot be empty.
  - Both FQDNs and IP addresses are supported for the servers field.
  - If the domain is modified, NIS servers must also be specified.
  - IPv6 must be enabled if IPv6 family addresses are specified for the servers field.
### Related ONTAP commands
* `vserver services name-service nis-domain modify`
### Learn more
* [`DOC /name-services/nis`](#docs-name-services-name-services_nis)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nis service modify")
        async def nis_service_modify(
        ) -> ResourceTable:
            """Modify an instance of a NisService resource

            Args:
                bound_servers: 
                query_bound_servers: 
                domain: The NIS domain to which this configuration belongs. 
                query_domain: The NIS domain to which this configuration belongs. 
                servers: A list of hostnames or IP addresses of NIS servers used by the NIS domain configuration. 
                query_servers: A list of hostnames or IP addresses of NIS servers used by the NIS domain configuration. 
            """

            kwargs = {}
            changes = {}
            if query_bound_servers is not None:
                kwargs["bound_servers"] = query_bound_servers
            if query_domain is not None:
                kwargs["domain"] = query_domain
            if query_servers is not None:
                kwargs["servers"] = query_servers

            if bound_servers is not None:
                changes["bound_servers"] = bound_servers
            if domain is not None:
                changes["domain"] = domain
            if servers is not None:
                changes["servers"] = servers

            if hasattr(NisService, "find"):
                resource = NisService.find(
                    **kwargs
                )
            else:
                resource = NisService()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify NisService: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the NIS domain configuration of an SVM. NIS can be removed as a source from ns-switch if NIS is not used for lookups.
### Related ONTAP commands
* `vserver services name-service nis-domain delete`
### Learn more
* [`DOC /name-services/nis`](#docs-name-services-name-services_nis)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nis service delete")
        async def nis_service_delete(
        ) -> None:
            """Delete an instance of a NisService resource

            Args:
                bound_servers: 
                domain: The NIS domain to which this configuration belongs. 
                servers: A list of hostnames or IP addresses of NIS servers used by the NIS domain configuration. 
            """

            kwargs = {}
            if bound_servers is not None:
                kwargs["bound_servers"] = bound_servers
            if domain is not None:
                kwargs["domain"] = domain
            if servers is not None:
                kwargs["servers"] = servers

            if hasattr(NisService, "find"):
                resource = NisService.find(
                    **kwargs
                )
            else:
                resource = NisService()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete NisService: %s" % err)


