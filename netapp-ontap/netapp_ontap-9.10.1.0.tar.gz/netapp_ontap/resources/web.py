r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

# Overview
You can use this API to update web services configurations and to retrieve current configurations.</br>
## Retrieving the current web services configuration
The cluster web GET API retrieves the current cluster-wide configuration.</br>
## Updating the current web services configuration
The cluster web PATCH API updates the current cluster-wide configuration.</br>
Once updated, ONTAP restarts the web services to apply the
changes. </br>
When updating the certificate, the certificate UUID of an existing certificate known to ONTAP must
be provided. The certificate must be of type "server".</br>
A "client-ca" certificate must be installed on ONTAP to enable "client_enabled".</br>
The following fields can be used to update the cluster-wide configuration:

* enabled
* http_port
* https_port
* http_enabled
* csrf.protection_enabled
* csrf.token.concurrent_limit
* csrf.token.idle_timeout
* csrf.token.max_timeout
* certificate.uuid
* client_enabled
* ocsp_enabled
## Examples
### Retrieving the cluster-wide web services configuration
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Web

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Web()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
Web(
    {
        "https_port": 443,
        "enabled": True,
        "certificate": {
            "name": "cert1",
            "uuid": "a3bb219d-4382-1fe0-9c06-1070568ea23d",
            "_links": {
                "self": {
                    "href": "/api/security/certificates/a3bb219d-4382-1fe0-9c06-1070568ea23d"
                }
            },
        },
        "client_enabled": False,
        "http_enabled": False,
        "ocsp_enabled": False,
        "state": "online",
        "csrf": {
            "token": {"concurrent_limit": 500, "max_timeout": 0, "idle_timeout": 900},
            "protection_enabled": True,
        },
        "http_port": 80,
        "_links": {"self": {"href": "/api/cluster/web"}},
    }
)

```
</div>
</div>

### Updating the cluster-wide web services configuration
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Web

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Web()
    resource.https_port = 446
    resource.csrf = {"token": {"concurrent_limit": 600}}
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


__all__ = ["Web", "WebSchema"]
__pdoc__ = {
    "WebSchema.resource": False,
    "Web.web_show": False,
    "Web.web_create": False,
    "Web.web_modify": False,
    "Web.web_delete": False,
}


class WebSchema(ResourceSchema):
    """The fields of the Web object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the web. """

    certificate = fields.Nested("netapp_ontap.models.web_certificate.WebCertificateSchema", data_key="certificate", unknown=EXCLUDE)
    r""" The certificate field of the web. """

    client_enabled = fields.Boolean(
        data_key="client_enabled",
    )
    r""" Indicates whether client authentication is enabled. """

    csrf = fields.Nested("netapp_ontap.models.web_csrf.WebCsrfSchema", data_key="csrf", unknown=EXCLUDE)
    r""" The csrf field of the web. """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Indicates whether remote clients can connect to the web services. """

    http_enabled = fields.Boolean(
        data_key="http_enabled",
    )
    r""" Indicates whether HTTP is enabled. """

    http_port = Size(
        data_key="http_port",
    )
    r""" HTTP port for cluster-level web services. """

    https_port = Size(
        data_key="https_port",
    )
    r""" HTTPS port for cluster-level web services. """

    ocsp_enabled = fields.Boolean(
        data_key="ocsp_enabled",
    )
    r""" Indicates whether online certificate status protocol verification is enabled. """

    per_address_limit = Size(
        data_key="per_address_limit",
        validate=integer_validation(minimum=24, maximum=999),
    )
    r""" The number of connections that can be processed concurrently from the same remote address.

Example: 42 """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['offline', 'partial', 'mixed', 'online', 'unclustered']),
    )
    r""" State of the cluster-level web services.

Valid choices:

* offline
* partial
* mixed
* online
* unclustered """

    wait_queue_capacity = Size(
        data_key="wait_queue_capacity",
    )
    r""" The maximum size of the wait queue for connections exceeding the per-address-limit. """

    @property
    def resource(self):
        return Web

    gettable_fields = [
        "links",
        "certificate",
        "client_enabled",
        "csrf",
        "enabled",
        "http_enabled",
        "http_port",
        "https_port",
        "ocsp_enabled",
        "per_address_limit",
        "state",
        "wait_queue_capacity",
    ]
    """links,certificate,client_enabled,csrf,enabled,http_enabled,http_port,https_port,ocsp_enabled,per_address_limit,state,wait_queue_capacity,"""

    patchable_fields = [
        "certificate",
        "client_enabled",
        "csrf",
        "enabled",
        "http_enabled",
        "http_port",
        "https_port",
        "ocsp_enabled",
        "per_address_limit",
        "wait_queue_capacity",
    ]
    """certificate,client_enabled,csrf,enabled,http_enabled,http_port,https_port,ocsp_enabled,per_address_limit,wait_queue_capacity,"""

    postable_fields = [
        "certificate",
        "client_enabled",
        "csrf",
        "enabled",
        "http_enabled",
        "http_port",
        "https_port",
        "ocsp_enabled",
        "per_address_limit",
        "wait_queue_capacity",
    ]
    """certificate,client_enabled,csrf,enabled,http_enabled,http_port,https_port,ocsp_enabled,per_address_limit,wait_queue_capacity,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Web.get_collection(fields=field)]
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
            raise NetAppRestError("Web modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Web(Resource):
    """Allows interaction with Web objects on the host"""

    _schema = WebSchema
    _path = "/api/cluster/web"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the web services configuration.
### Learn more
* [`DOC /cluster/web`](#docs-cluster-cluster_web)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="web show")
        def web_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single Web resource

            Args:
                client_enabled: Indicates whether client authentication is enabled.
                enabled: Indicates whether remote clients can connect to the web services.
                http_enabled: Indicates whether HTTP is enabled.
                http_port: HTTP port for cluster-level web services.
                https_port: HTTPS port for cluster-level web services.
                ocsp_enabled: Indicates whether online certificate status protocol verification is enabled.
                per_address_limit: The number of connections that can be processed concurrently from the same remote address.
                state: State of the cluster-level web services.
                wait_queue_capacity: The maximum size of the wait queue for connections exceeding the per-address-limit.
            """

            kwargs = {}
            if client_enabled is not None:
                kwargs["client_enabled"] = client_enabled
            if enabled is not None:
                kwargs["enabled"] = enabled
            if http_enabled is not None:
                kwargs["http_enabled"] = http_enabled
            if http_port is not None:
                kwargs["http_port"] = http_port
            if https_port is not None:
                kwargs["https_port"] = https_port
            if ocsp_enabled is not None:
                kwargs["ocsp_enabled"] = ocsp_enabled
            if per_address_limit is not None:
                kwargs["per_address_limit"] = per_address_limit
            if state is not None:
                kwargs["state"] = state
            if wait_queue_capacity is not None:
                kwargs["wait_queue_capacity"] = wait_queue_capacity
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = Web(
                **kwargs
            )
            resource.get()
            return [resource]


    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the web services configuration.
### Related ONTAP commands
* `system services web modify`

### Learn more
* [`DOC /cluster/web`](#docs-cluster-cluster_web)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="web modify")
        async def web_modify(
        ) -> ResourceTable:
            """Modify an instance of a Web resource

            Args:
                client_enabled: Indicates whether client authentication is enabled.
                query_client_enabled: Indicates whether client authentication is enabled.
                enabled: Indicates whether remote clients can connect to the web services.
                query_enabled: Indicates whether remote clients can connect to the web services.
                http_enabled: Indicates whether HTTP is enabled.
                query_http_enabled: Indicates whether HTTP is enabled.
                http_port: HTTP port for cluster-level web services.
                query_http_port: HTTP port for cluster-level web services.
                https_port: HTTPS port for cluster-level web services.
                query_https_port: HTTPS port for cluster-level web services.
                ocsp_enabled: Indicates whether online certificate status protocol verification is enabled.
                query_ocsp_enabled: Indicates whether online certificate status protocol verification is enabled.
                per_address_limit: The number of connections that can be processed concurrently from the same remote address.
                query_per_address_limit: The number of connections that can be processed concurrently from the same remote address.
                state: State of the cluster-level web services.
                query_state: State of the cluster-level web services.
                wait_queue_capacity: The maximum size of the wait queue for connections exceeding the per-address-limit.
                query_wait_queue_capacity: The maximum size of the wait queue for connections exceeding the per-address-limit.
            """

            kwargs = {}
            changes = {}
            if query_client_enabled is not None:
                kwargs["client_enabled"] = query_client_enabled
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_http_enabled is not None:
                kwargs["http_enabled"] = query_http_enabled
            if query_http_port is not None:
                kwargs["http_port"] = query_http_port
            if query_https_port is not None:
                kwargs["https_port"] = query_https_port
            if query_ocsp_enabled is not None:
                kwargs["ocsp_enabled"] = query_ocsp_enabled
            if query_per_address_limit is not None:
                kwargs["per_address_limit"] = query_per_address_limit
            if query_state is not None:
                kwargs["state"] = query_state
            if query_wait_queue_capacity is not None:
                kwargs["wait_queue_capacity"] = query_wait_queue_capacity

            if client_enabled is not None:
                changes["client_enabled"] = client_enabled
            if enabled is not None:
                changes["enabled"] = enabled
            if http_enabled is not None:
                changes["http_enabled"] = http_enabled
            if http_port is not None:
                changes["http_port"] = http_port
            if https_port is not None:
                changes["https_port"] = https_port
            if ocsp_enabled is not None:
                changes["ocsp_enabled"] = ocsp_enabled
            if per_address_limit is not None:
                changes["per_address_limit"] = per_address_limit
            if state is not None:
                changes["state"] = state
            if wait_queue_capacity is not None:
                changes["wait_queue_capacity"] = wait_queue_capacity

            if hasattr(Web, "find"):
                resource = Web.find(
                    **kwargs
                )
            else:
                resource = Web()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify Web: %s" % err)



