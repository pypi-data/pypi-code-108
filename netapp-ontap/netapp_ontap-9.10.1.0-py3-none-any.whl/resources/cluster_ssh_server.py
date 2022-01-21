r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
ONTAP supports SSH server that can be accessed from any standard SSH client. A user account needs to be associated with SSH as the application (refer the documentation for <i>api/security/accounts</i> [`DOC /security/accounts`](#docs-security-security_accounts)). Upon connecting from a client, the user is authenticated and a command line shell is presented.<br/>
This endpoint is used to retrieve or modify the SSH configuration at the cluster level. The configuration consists of SSH security parameters (security algorithms and maximum authentication retry attempts allowed before closing the connection) and SSH connection limits.<br/>
The security algorithms include SSH key exchange algorithms, ciphers for payload encryption, and MAC algorithms. This configuration is the default for all newly created SVMs; existing SVM configurations are not impacted.
The SSH connection limits include maximum connections per second, maximum simultaneous sessions from the same client host, and overall maximum SSH connections at any given point in time. The connection limits are per node and will be the same for all nodes in the cluster.
## Examples
### Updating the SSH security parameters
Specify the algorithms in the body of the PATCH request.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterSshServer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterSshServer()
    resource.ciphers = ["aes256_ctr", "aes192_ctr"]
    resource.key_exchange_algorithms = [
        "diffie_hellman_group_exchange_sha256",
        "diffie_hellman_group14_sha1",
    ]
    resource.mac_algorithms = ["hmac_sha2_512_etm", "umac_128_etm"]
    resource.max_authentication_retry_count = 3
    resource.patch()

```

### Updating the SSH connection limits
Specify the connection limits in the body of the PATCH request.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterSshServer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterSshServer()
    resource.connections_per_second = 8
    resource.max_instances = 10
    resource.per_source_limit = 5
    resource.patch()

```

### Retrieving the cluster SSH server configuration
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterSshServer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterSshServer()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
ClusterSshServer(
    {
        "connections_per_second": 8,
        "mac_algorithms": ["hmac_sha2_512_etm", "umac_128_etm"],
        "ciphers": ["aes256_ctr", "aes192_ctr"],
        "max_instances": 10,
        "max_authentication_retry_count": 3,
        "per_source_limit": 5,
        "key_exchange_algorithms": [
            "diffie_hellman_group_exchange_sha256",
            "diffie_hellman_group14_sha1",
        ],
        "_links": {"self": {"href": "/api/security/ssh"}},
    }
)

```
</div>
</div>

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


__all__ = ["ClusterSshServer", "ClusterSshServerSchema"]
__pdoc__ = {
    "ClusterSshServerSchema.resource": False,
    "ClusterSshServer.cluster_ssh_server_show": False,
    "ClusterSshServer.cluster_ssh_server_create": False,
    "ClusterSshServer.cluster_ssh_server_modify": False,
    "ClusterSshServer.cluster_ssh_server_delete": False,
}


class ClusterSshServerSchema(ResourceSchema):
    """The fields of the ClusterSshServer object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the cluster_ssh_server. """

    ciphers = fields.List(fields.Str, data_key="ciphers")
    r""" Ciphers for encrypting the data.

Example: ["aes256_ctr","aes192_ctr","aes128_ctr"] """

    connections_per_second = Size(
        data_key="connections_per_second",
        validate=integer_validation(minimum=1, maximum=70),
    )
    r""" Maximum connections allowed per second. """

    key_exchange_algorithms = fields.List(fields.Str, data_key="key_exchange_algorithms")
    r""" Key exchange algorithms.

Example: ["diffie_hellman_group_exchange_sha256","diffie_hellman_group14_sha1"] """

    mac_algorithms = fields.List(fields.Str, data_key="mac_algorithms")
    r""" MAC algorithms.

Example: ["hmac_sha1","hmac_sha2_512_etm"] """

    max_authentication_retry_count = Size(
        data_key="max_authentication_retry_count",
        validate=integer_validation(minimum=2, maximum=6),
    )
    r""" Maximum authentication retries allowed before closing the connection. """

    max_instances = Size(
        data_key="max_instances",
        validate=integer_validation(minimum=1, maximum=128),
    )
    r""" Maximum possible simultaneous connections. """

    per_source_limit = Size(
        data_key="per_source_limit",
        validate=integer_validation(minimum=1, maximum=64),
    )
    r""" Maximum connections from the same client host. """

    @property
    def resource(self):
        return ClusterSshServer

    gettable_fields = [
        "links",
        "ciphers",
        "connections_per_second",
        "key_exchange_algorithms",
        "mac_algorithms",
        "max_authentication_retry_count",
        "max_instances",
        "per_source_limit",
    ]
    """links,ciphers,connections_per_second,key_exchange_algorithms,mac_algorithms,max_authentication_retry_count,max_instances,per_source_limit,"""

    patchable_fields = [
        "ciphers",
        "connections_per_second",
        "key_exchange_algorithms",
        "mac_algorithms",
        "max_authentication_retry_count",
        "max_instances",
        "per_source_limit",
    ]
    """ciphers,connections_per_second,key_exchange_algorithms,mac_algorithms,max_authentication_retry_count,max_instances,per_source_limit,"""

    postable_fields = [
        "ciphers",
        "connections_per_second",
        "key_exchange_algorithms",
        "mac_algorithms",
        "max_authentication_retry_count",
        "max_instances",
        "per_source_limit",
    ]
    """ciphers,connections_per_second,key_exchange_algorithms,mac_algorithms,max_authentication_retry_count,max_instances,per_source_limit,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in ClusterSshServer.get_collection(fields=field)]
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
            raise NetAppRestError("ClusterSshServer modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class ClusterSshServer(Resource):
    """Allows interaction with ClusterSshServer objects on the host"""

    _schema = ClusterSshServerSchema
    _path = "/api/security/ssh"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the cluster SSH server ciphers, MAC algorithms, key exchange algorithms, and connection limits.
### Related ONTAP commands
* `security ssh`
* `security protocol ssh`

### Learn more
* [`DOC /security/ssh`](#docs-security-security_ssh)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster ssh server show")
        def cluster_ssh_server_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single ClusterSshServer resource

            Args:
                ciphers: Ciphers for encrypting the data.
                connections_per_second: Maximum connections allowed per second.
                key_exchange_algorithms: Key exchange algorithms.
                mac_algorithms: MAC algorithms.
                max_authentication_retry_count: Maximum authentication retries allowed before closing the connection.
                max_instances: Maximum possible simultaneous connections.
                per_source_limit: Maximum connections from the same client host.
            """

            kwargs = {}
            if ciphers is not None:
                kwargs["ciphers"] = ciphers
            if connections_per_second is not None:
                kwargs["connections_per_second"] = connections_per_second
            if key_exchange_algorithms is not None:
                kwargs["key_exchange_algorithms"] = key_exchange_algorithms
            if mac_algorithms is not None:
                kwargs["mac_algorithms"] = mac_algorithms
            if max_authentication_retry_count is not None:
                kwargs["max_authentication_retry_count"] = max_authentication_retry_count
            if max_instances is not None:
                kwargs["max_instances"] = max_instances
            if per_source_limit is not None:
                kwargs["per_source_limit"] = per_source_limit
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = ClusterSshServer(
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
        r"""Updates the SSH server setting for a cluster.
### Optional parameters
* `ciphers` - Encryption algorithms for the payload
* `key_exchange_algorithms` - SSH key exchange algorithms
* `mac_algorithms` - MAC algorithms
* `max_authentication_retry_count` - Maximum authentication retries allowed before closing the connection
* `connections_per_second` - Maximum allowed connections per second
* `max_instances` - Maximum allowed connections per node
* `per_source_limit` - Maximum allowed connections from the same client host
### Related ONTAP commands
* `security ssh`
* `security protocol ssh`

### Learn more
* [`DOC /security/ssh`](#docs-security-security_ssh)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster ssh server modify")
        async def cluster_ssh_server_modify(
        ) -> ResourceTable:
            """Modify an instance of a ClusterSshServer resource

            Args:
                ciphers: Ciphers for encrypting the data.
                query_ciphers: Ciphers for encrypting the data.
                connections_per_second: Maximum connections allowed per second.
                query_connections_per_second: Maximum connections allowed per second.
                key_exchange_algorithms: Key exchange algorithms.
                query_key_exchange_algorithms: Key exchange algorithms.
                mac_algorithms: MAC algorithms.
                query_mac_algorithms: MAC algorithms.
                max_authentication_retry_count: Maximum authentication retries allowed before closing the connection.
                query_max_authentication_retry_count: Maximum authentication retries allowed before closing the connection.
                max_instances: Maximum possible simultaneous connections.
                query_max_instances: Maximum possible simultaneous connections.
                per_source_limit: Maximum connections from the same client host.
                query_per_source_limit: Maximum connections from the same client host.
            """

            kwargs = {}
            changes = {}
            if query_ciphers is not None:
                kwargs["ciphers"] = query_ciphers
            if query_connections_per_second is not None:
                kwargs["connections_per_second"] = query_connections_per_second
            if query_key_exchange_algorithms is not None:
                kwargs["key_exchange_algorithms"] = query_key_exchange_algorithms
            if query_mac_algorithms is not None:
                kwargs["mac_algorithms"] = query_mac_algorithms
            if query_max_authentication_retry_count is not None:
                kwargs["max_authentication_retry_count"] = query_max_authentication_retry_count
            if query_max_instances is not None:
                kwargs["max_instances"] = query_max_instances
            if query_per_source_limit is not None:
                kwargs["per_source_limit"] = query_per_source_limit

            if ciphers is not None:
                changes["ciphers"] = ciphers
            if connections_per_second is not None:
                changes["connections_per_second"] = connections_per_second
            if key_exchange_algorithms is not None:
                changes["key_exchange_algorithms"] = key_exchange_algorithms
            if mac_algorithms is not None:
                changes["mac_algorithms"] = mac_algorithms
            if max_authentication_retry_count is not None:
                changes["max_authentication_retry_count"] = max_authentication_retry_count
            if max_instances is not None:
                changes["max_instances"] = max_instances
            if per_source_limit is not None:
                changes["per_source_limit"] = per_source_limit

            if hasattr(ClusterSshServer, "find"):
                resource = ClusterSshServer.find(
                    **kwargs
                )
            else:
                resource = ClusterSshServer()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify ClusterSshServer: %s" % err)



