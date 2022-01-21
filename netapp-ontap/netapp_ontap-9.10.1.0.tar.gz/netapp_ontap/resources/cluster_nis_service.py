r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
NIS servers are used to authenticate user and client computers. NIS domain name and NIS server information is required to configure NIS. This API retrieves and manages NIS server configurations.
## Examples
### Retrieving cluster NIS information
The cluster NIS GET request retrieves the NIS configuration of the cluster.<br>
The following example shows how a GET request is used to retrieve the cluster NIS configuration:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterNisService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterNisService()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
ClusterNisService(
    {
        "domain": "domainA.example.com",
        "bound_servers": ["10.10.10.10"],
        "servers": ["10.10.10.10", "example.com"],
    }
)

```
</div>
</div>

### Creating the cluster NIS configuration
The cluster NIS POST request creates a NIS configuration for the cluster.<br>
The following example shows how a POST request is used to create a cluster NIS configuration:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterNisService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterNisService()
    resource.domain = "domainA.example.com"
    resource.servers = ["10.10.10.10", "example.com"]
    resource.post(hydrate=True)
    print(resource)

```

### Updating the cluster NIS configuration
The cluster NIS PATCH request updates the NIS configuration of the cluster.<br>
The following example shows how to update the domain:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterNisService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterNisService()
    resource.domain = "domainC.example.com"
    resource.servers = ["13.13.13.13"]
    resource.patch()

```

The following example shows how to update the server:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterNisService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterNisService()
    resource.servers = ["14.14.14.14"]
    resource.patch()

```

## Deleting the cluster NIS configuration
The cluster NIS DELETE request deletes the NIS configuration of the cluster.<br>
The following example shows how a DELETE request is used to delete the cluster NIS configuration:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterNisService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterNisService()
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


__all__ = ["ClusterNisService", "ClusterNisServiceSchema"]
__pdoc__ = {
    "ClusterNisServiceSchema.resource": False,
    "ClusterNisService.cluster_nis_service_show": False,
    "ClusterNisService.cluster_nis_service_create": False,
    "ClusterNisService.cluster_nis_service_modify": False,
    "ClusterNisService.cluster_nis_service_delete": False,
}


class ClusterNisServiceSchema(ResourceSchema):
    """The fields of the ClusterNisService object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the cluster_nis_service. """

    bound_servers = fields.List(fields.Str, data_key="bound_servers")
    r""" The bound_servers field of the cluster_nis_service. """

    domain = fields.Str(
        data_key="domain",
        validate=len_validation(minimum=1, maximum=64),
    )
    r""" The NIS domain to which this configuration belongs. """

    servers = fields.List(fields.Str, data_key="servers")
    r""" A list of hostnames or IP addresses of NIS servers used
by the NIS domain configuration. """

    @property
    def resource(self):
        return ClusterNisService

    gettable_fields = [
        "links",
        "bound_servers",
        "domain",
        "servers",
    ]
    """links,bound_servers,domain,servers,"""

    patchable_fields = [
        "domain",
        "servers",
    ]
    """domain,servers,"""

    postable_fields = [
        "domain",
        "servers",
    ]
    """domain,servers,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in ClusterNisService.get_collection(fields=field)]
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
            raise NetAppRestError("ClusterNisService modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class ClusterNisService(Resource):
    """Allows interaction with ClusterNisService objects on the host"""

    _schema = ClusterNisServiceSchema
    _path = "/api/security/authentication/cluster/nis"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the NIS configuration of the cluster. Both NIS domain and servers are displayed by default.
The `bound_servers` property indicates the successfully bound NIS servers.

### Learn more
* [`DOC /security/authentication/cluster/nis`](#docs-security-security_authentication_cluster_nis)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster nis service show")
        def cluster_nis_service_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single ClusterNisService resource

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

            resource = ClusterNisService(
                **kwargs
            )
            resource.get()
            return [resource]

    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""The cluster can have one NIS server configuration. Specify the NIS domain and NIS servers as input. Domain name and servers fields cannot be empty.
Both FQDNs and IP addresses are supported for the `server` property. IPv6 must be enabled if IPv6 family addresses are specified in the `server` property. A maximum of ten NIS servers are supported.
### Required properties
* `domain` - NIS domain to which this configuration belongs.
* `servers` - List of hostnames or IP addresses of NIS servers used by the NIS domain configuration.

### Learn more
* [`DOC /security/authentication/cluster/nis`](#docs-security-security_authentication_cluster_nis)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster nis service create")
        async def cluster_nis_service_create(
        ) -> ResourceTable:
            """Create an instance of a ClusterNisService resource

            Args:
                links: 
                bound_servers: 
                domain: The NIS domain to which this configuration belongs. 
                servers: A list of hostnames or IP addresses of NIS servers used by the NIS domain configuration. 
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

            resource = ClusterNisService(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create ClusterNisService: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Both NIS domain and servers can be updated. Domains and servers cannot be empty. Both FQDNs and IP addresses are supported for the 'servers' field. If the domain is updated, NIS servers must also be specified. IPv6 must be enabled if IPv6 family addresses are specified for the `servers` property.<br/>

### Learn more
* [`DOC /security/authentication/cluster/nis`](#docs-security-security_authentication_cluster_nis)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster nis service modify")
        async def cluster_nis_service_modify(
        ) -> ResourceTable:
            """Modify an instance of a ClusterNisService resource

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

            if hasattr(ClusterNisService, "find"):
                resource = ClusterNisService.find(
                    **kwargs
                )
            else:
                resource = ClusterNisService()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify ClusterNisService: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the NIS configuration of the cluster. NIS can be removed as a source from ns-switch if NIS is not used for lookups.

### Learn more
* [`DOC /security/authentication/cluster/nis`](#docs-security-security_authentication_cluster_nis)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster nis service delete")
        async def cluster_nis_service_delete(
        ) -> None:
            """Delete an instance of a ClusterNisService resource

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

            if hasattr(ClusterNisService, "find"):
                resource = ClusterNisService.find(
                    **kwargs
                )
            else:
                resource = ClusterNisService()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete ClusterNisService: %s" % err)


