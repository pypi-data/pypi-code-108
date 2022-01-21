r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
You can use this API to add external NTP servers to a cluster, update the configuration, use NTP keys, and retrieve the
current NTP server configuration.
## Adding an NTP server to a cluster
To add an NTP server to a cluster, issue a POST /cluster/ntp/servers request.
### Fields used for adding an NTP server
Except for the name of the NTP server (host name or IP address), which is specified by the server, all fields are optional:

* `version`
* `key`
###
If the key is provided in POST, `authentication_enabled` is set to `true` by default.
## Examples
### Adding an NTP server
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NtpServer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NtpServer()
    resource.server = "time.nist.gov"
    resource.post(hydrate=True)
    print(resource)

```

---
### Adding an NTP server with an authentication key
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NtpServer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NtpServer()
    resource.server = "time.nist.gov"
    resource.key = {"id": 10}
    resource.post(hydrate=True)
    print(resource)

```

---
### Enabling a previously configured shared key (ID, type, and value) for an NTP server
A combination of key number or identifier (ID), type of key, and shared key value is created with /api/cluster/ntp/keys.
This operation will validate the NTP authentication works.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NtpServer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NtpServer(server="time.nist.gov")
    resource.key = {"id": 10}
    resource.authentication_enabled = True
    resource.patch()

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


__all__ = ["NtpServer", "NtpServerSchema"]
__pdoc__ = {
    "NtpServerSchema.resource": False,
    "NtpServer.ntp_server_show": False,
    "NtpServer.ntp_server_create": False,
    "NtpServer.ntp_server_modify": False,
    "NtpServer.ntp_server_delete": False,
}


class NtpServerSchema(ResourceSchema):
    """The fields of the NtpServer object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the ntp_server. """

    authentication_enabled = fields.Boolean(
        data_key="authentication_enabled",
    )
    r""" Set NTP symmetric authentication on (true) or off (false).

Example: true """

    key = fields.Nested("netapp_ontap.resources.ntp_key.NtpKeySchema", data_key="key", unknown=EXCLUDE)
    r""" The key field of the ntp_server. """

    server = fields.Str(
        data_key="server",
    )
    r""" NTP server host name, IPv4, or IPv6 address.

Example: time.nist.gov """

    version = fields.Str(
        data_key="version",
        validate=enum_validation(['3', '4', 'auto']),
    )
    r""" NTP protocol version for server. Valid versions are 3, 4, or auto.

Valid choices:

* 3
* 4
* auto """

    @property
    def resource(self):
        return NtpServer

    gettable_fields = [
        "links",
        "authentication_enabled",
        "key.links",
        "key.id",
        "server",
        "version",
    ]
    """links,authentication_enabled,key.links,key.id,server,version,"""

    patchable_fields = [
        "authentication_enabled",
        "key.id",
        "version",
    ]
    """authentication_enabled,key.id,version,"""

    postable_fields = [
        "key.id",
        "server",
        "version",
    ]
    """key.id,server,version,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NtpServer.get_collection(fields=field)]
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
            raise NetAppRestError("NtpServer modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NtpServer(Resource):
    """Allows interaction with NtpServer objects on the host"""

    _schema = NtpServerSchema
    _path = "/api/cluster/ntp/servers"
    _keys = ["server"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the collection of external NTP time servers ONTAP uses for time adjustment and correction.
### Related ONTAP commands
* `cluster time-service ntp server show`
### Learn more
* [`DOC /cluster/ntp/servers`](#docs-cluster-cluster_ntp_servers)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ntp server show")
        def ntp_server_show(
            fields: List[Choices.define(["authentication_enabled", "server", "version", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of NtpServer resources

            Args:
                authentication_enabled: Set NTP symmetric authentication on (true) or off (false).
                server: NTP server host name, IPv4, or IPv6 address.
                version: NTP protocol version for server. Valid versions are 3, 4, or auto.
            """

            kwargs = {}
            if authentication_enabled is not None:
                kwargs["authentication_enabled"] = authentication_enabled
            if server is not None:
                kwargs["server"] = server
            if version is not None:
                kwargs["version"] = version
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return NtpServer.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NtpServer resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["NtpServer"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the configuration of an NTP server used by the ONTAP cluster after validation.
Patchable fields are:
* `version`
* `key.id`
* `authentication_enabled`
</br>
If `authentication_enabled` is modified to `false`, the associated NTP key is removed from the server instance.
If `authentication_enabled` is modified to `true`, you must provide an NTP key ID in the PATCH body.
### Related ONTAP commands
* `cluster time-service ntp server modify`
### Learn more
* [`DOC /cluster/ntp/servers`](#docs-cluster-cluster_ntp_servers)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["NtpServer"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["NtpServer"], NetAppResponse]:
        r"""Validates the provided external NTP time server for usage and configures ONTAP so that all nodes in the cluster use it.
The required fields are:
* `server`
### Default property values
If not specified in POST, the following default property values are assigned:
* `version` - auto
* `key` - not set
###
If the key is provided in POST, `authentication_enabled` is set to `true` by default.
### Related ONTAP commands
* `cluster time-service ntp server create`
### Learn more
* [`DOC /cluster/ntp/servers`](#docs-cluster-cluster_ntp_servers)
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
        records: Iterable["NtpServer"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an external NTP server used by ONTAP.
### Related ONTAP commands
* `cluster time-service ntp server delete`
### Learn more
* [`DOC /cluster/ntp/servers`](#docs-cluster-cluster_ntp_servers)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the collection of external NTP time servers ONTAP uses for time adjustment and correction.
### Related ONTAP commands
* `cluster time-service ntp server show`
### Learn more
* [`DOC /cluster/ntp/servers`](#docs-cluster-cluster_ntp_servers)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the configuration of an external NTP server used by ONTAP.
### Related ONTAP commands
* `cluster time-service ntp server show`
### Learn more
* [`DOC /cluster/ntp/servers`](#docs-cluster-cluster_ntp_servers)
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
        r"""Validates the provided external NTP time server for usage and configures ONTAP so that all nodes in the cluster use it.
The required fields are:
* `server`
### Default property values
If not specified in POST, the following default property values are assigned:
* `version` - auto
* `key` - not set
###
If the key is provided in POST, `authentication_enabled` is set to `true` by default.
### Related ONTAP commands
* `cluster time-service ntp server create`
### Learn more
* [`DOC /cluster/ntp/servers`](#docs-cluster-cluster_ntp_servers)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ntp server create")
        async def ntp_server_create(
        ) -> ResourceTable:
            """Create an instance of a NtpServer resource

            Args:
                links: 
                authentication_enabled: Set NTP symmetric authentication on (true) or off (false).
                key: 
                server: NTP server host name, IPv4, or IPv6 address.
                version: NTP protocol version for server. Valid versions are 3, 4, or auto.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if authentication_enabled is not None:
                kwargs["authentication_enabled"] = authentication_enabled
            if key is not None:
                kwargs["key"] = key
            if server is not None:
                kwargs["server"] = server
            if version is not None:
                kwargs["version"] = version

            resource = NtpServer(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create NtpServer: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the configuration of an NTP server used by the ONTAP cluster after validation.
Patchable fields are:
* `version`
* `key.id`
* `authentication_enabled`
</br>
If `authentication_enabled` is modified to `false`, the associated NTP key is removed from the server instance.
If `authentication_enabled` is modified to `true`, you must provide an NTP key ID in the PATCH body.
### Related ONTAP commands
* `cluster time-service ntp server modify`
### Learn more
* [`DOC /cluster/ntp/servers`](#docs-cluster-cluster_ntp_servers)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ntp server modify")
        async def ntp_server_modify(
        ) -> ResourceTable:
            """Modify an instance of a NtpServer resource

            Args:
                authentication_enabled: Set NTP symmetric authentication on (true) or off (false).
                query_authentication_enabled: Set NTP symmetric authentication on (true) or off (false).
                server: NTP server host name, IPv4, or IPv6 address.
                query_server: NTP server host name, IPv4, or IPv6 address.
                version: NTP protocol version for server. Valid versions are 3, 4, or auto.
                query_version: NTP protocol version for server. Valid versions are 3, 4, or auto.
            """

            kwargs = {}
            changes = {}
            if query_authentication_enabled is not None:
                kwargs["authentication_enabled"] = query_authentication_enabled
            if query_server is not None:
                kwargs["server"] = query_server
            if query_version is not None:
                kwargs["version"] = query_version

            if authentication_enabled is not None:
                changes["authentication_enabled"] = authentication_enabled
            if server is not None:
                changes["server"] = server
            if version is not None:
                changes["version"] = version

            if hasattr(NtpServer, "find"):
                resource = NtpServer.find(
                    **kwargs
                )
            else:
                resource = NtpServer()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify NtpServer: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an external NTP server used by ONTAP.
### Related ONTAP commands
* `cluster time-service ntp server delete`
### Learn more
* [`DOC /cluster/ntp/servers`](#docs-cluster-cluster_ntp_servers)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ntp server delete")
        async def ntp_server_delete(
        ) -> None:
            """Delete an instance of a NtpServer resource

            Args:
                authentication_enabled: Set NTP symmetric authentication on (true) or off (false).
                server: NTP server host name, IPv4, or IPv6 address.
                version: NTP protocol version for server. Valid versions are 3, 4, or auto.
            """

            kwargs = {}
            if authentication_enabled is not None:
                kwargs["authentication_enabled"] = authentication_enabled
            if server is not None:
                kwargs["server"] = server
            if version is not None:
                kwargs["version"] = version

            if hasattr(NtpServer, "find"):
                resource = NtpServer.find(
                    **kwargs
                )
            else:
                resource = NtpServer()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete NtpServer: %s" % err)


