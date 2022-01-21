r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
ONTAP connected clients show functionality is mainly used to provide a list of currently connected NFS clients. It also provides a potential list of other NFS clients that can be connected but are currently idle.<p/>
The following are details of the fields retrieved for the Connected Clients GET API:<p/>
node.name: The node name hosting this record; basically the node hosting the "server_ip".
node.uuid: The node UUID hosting this record; basically the node hosting the "server_ip".
svm.name: The svm name to which the "server_ip" belongs to.
svm.uuid: The svm uuid to which the "server_ip" belongs to.
server_ip: All clients that are connected to this interface are displayed in rows.
client_ip: The IP address of the client that is connected to the interface.
volume.name: The name of the volume the client is accessing.
volume.uuid: The UUID of the volume the client is accessing. This field is expensive field and will be fetched in advance privilege level.
protocol: The NFS protocol version over which client is accessing the volume.
export_policy.id: The export policy ID associated with the volume.
export_policy.name: The export policy name associated with the volume.
idle_duration: The time elapsed since the last request was sent by the client for this volume.
local_request_count: A counter that tracks requests that are sent to the volume with fast-path to local node.
remote_request_count: A counter that tracks requests that are sent to the volume with slow-path to remote node.
## Example
### Retrieves connected client information
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NfsClients

with HostConnection(
    "<cluster-mgmt-ip>", username="admin", password="password", verify=False
):
    print(list(NfsClients.get_collection(return_timeout=15)))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    NfsClients(
        {
            "server_ip": "10.140.72.214",
            "svm": {"uuid": "c642db55-b8d0-11e9-9ad1-0050568e8480", "name": "vs1"},
            "volume": {"uuid": "c6bbc6f2-b8d0-11e9-9ad1-0050568e8480", "name": "rvol1"},
            "protocol": "nfs4",
            "node": {"uuid": "cc282893-b82f-11e9-a3ad-0050568e8480", "name": "vsim1"},
            "client_ip": "10.140.137.57",
        }
    ),
    NfsClients(
        {
            "server_ip": "10.140.72.214",
            "svm": {"uuid": "c642db55-b8d0-11e9-9ad1-0050568e8480", "name": "vs1"},
            "volume": {"uuid": "d28d1999-b8d0-11e9-9ad1-0050568e8480", "name": "vol1"},
            "protocol": "nfs3",
            "node": {"uuid": "cc282893-b82f-11e9-a3ad-0050568e8480", "name": "vsim1"},
            "client_ip": "10.140.137.57",
        }
    ),
    NfsClients(
        {
            "server_ip": "10.140.72.214",
            "svm": {"uuid": "c642db55-b8d0-11e9-9ad1-0050568e8480", "name": "vs1"},
            "volume": {"uuid": "d28d1999-b8d0-11e9-9ad1-0050568e8480", "name": "vol1"},
            "protocol": "nfs4",
            "node": {"uuid": "cc282893-b82f-11e9-a3ad-0050568e8480", "name": "vsim1"},
            "client_ip": "10.140.137.57",
        }
    ),
]

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


__all__ = ["NfsClients", "NfsClientsSchema"]
__pdoc__ = {
    "NfsClientsSchema.resource": False,
    "NfsClients.nfs_clients_show": False,
    "NfsClients.nfs_clients_create": False,
    "NfsClients.nfs_clients_modify": False,
    "NfsClients.nfs_clients_delete": False,
}


class NfsClientsSchema(ResourceSchema):
    """The fields of the NfsClients object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the nfs_clients. """

    client_ip = fields.Str(
        data_key="client_ip",
    )
    r""" Specifies IP address of the client. """

    export_policy = fields.Nested("netapp_ontap.resources.export_policy.ExportPolicySchema", data_key="export_policy", unknown=EXCLUDE)
    r""" The export_policy field of the nfs_clients. """

    idle_duration = fields.Str(
        data_key="idle_duration",
    )
    r""" Specifies an ISO-8601 format of date and time to retrieve the idle time duration in hours, minutes, and seconds format.


Example: P4DT84H30M5S """

    local_request_count = Size(
        data_key="local_request_count",
    )
    r""" A counter that tracks requests that are sent to the volume with fast-path to local node. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the nfs_clients. """

    protocol = fields.Str(
        data_key="protocol",
        validate=enum_validation(['nfs', 'nfs3', 'nfs4', 'nfs4.1']),
    )
    r""" The NFS protocol version over which client is accessing the volume. The following values are supported:

* nfs - All NFS versions are considered
* nfs3 - NFS version 3 protocol
* nfs4 - NFS version 4 protocol
* nfs4.1 - NFS version 4 minor version 1 protocol


Valid choices:

* nfs
* nfs3
* nfs4
* nfs4.1 """

    remote_request_count = Size(
        data_key="remote_request_count",
    )
    r""" A counter that tracks requests that are sent to the volume with slow-path to remote node. """

    server_ip = fields.Str(
        data_key="server_ip",
    )
    r""" Specifies the IP address of the server. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the nfs_clients. """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the nfs_clients. """

    @property
    def resource(self):
        return NfsClients

    gettable_fields = [
        "links",
        "client_ip",
        "export_policy.links",
        "export_policy.id",
        "export_policy.name",
        "idle_duration",
        "local_request_count",
        "node.links",
        "node.name",
        "node.uuid",
        "protocol",
        "remote_request_count",
        "server_ip",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,client_ip,export_policy.links,export_policy.id,export_policy.name,idle_duration,local_request_count,node.links,node.name,node.uuid,protocol,remote_request_count,server_ip,svm.links,svm.name,svm.uuid,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "client_ip",
        "export_policy.id",
        "export_policy.name",
        "idle_duration",
        "local_request_count",
        "node.name",
        "node.uuid",
        "remote_request_count",
        "server_ip",
        "svm.name",
        "svm.uuid",
        "volume.name",
        "volume.uuid",
    ]
    """client_ip,export_policy.id,export_policy.name,idle_duration,local_request_count,node.name,node.uuid,remote_request_count,server_ip,svm.name,svm.uuid,volume.name,volume.uuid,"""

    postable_fields = [
        "client_ip",
        "export_policy.id",
        "export_policy.name",
        "idle_duration",
        "local_request_count",
        "node.name",
        "node.uuid",
        "remote_request_count",
        "server_ip",
        "svm.name",
        "svm.uuid",
        "volume.name",
        "volume.uuid",
    ]
    """client_ip,export_policy.id,export_policy.name,idle_duration,local_request_count,node.name,node.uuid,remote_request_count,server_ip,svm.name,svm.uuid,volume.name,volume.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NfsClients.get_collection(fields=field)]
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
            raise NetAppRestError("NfsClients modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NfsClients(Resource):
    """Allows interaction with NfsClients objects on the host"""

    _schema = NfsClientsSchema
    _path = "/api/protocols/nfs/connected-clients"

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the NFS configuration of SVMs.
### Expensive properties
export_policy.id is expensive field. It is not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `export_policy.id`

### Learn more
* [`DOC /protocols/nfs/connected-clients`](#docs-NAS-protocols_nfs_connected-clients)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nfs clients show")
        def nfs_clients_show(
            fields: List[Choices.define(["client_ip", "idle_duration", "local_request_count", "protocol", "remote_request_count", "server_ip", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of NfsClients resources

            Args:
                client_ip: Specifies IP address of the client. 
                idle_duration: Specifies an ISO-8601 format of date and time to retrieve the idle time duration in hours, minutes, and seconds format. 
                local_request_count: A counter that tracks requests that are sent to the volume with fast-path to local node. 
                protocol: The NFS protocol version over which client is accessing the volume. The following values are supported: * nfs - All NFS versions are considered * nfs3 - NFS version 3 protocol * nfs4 - NFS version 4 protocol * nfs4.1 - NFS version 4 minor version 1 protocol 
                remote_request_count: A counter that tracks requests that are sent to the volume with slow-path to remote node. 
                server_ip: Specifies the IP address of the server. 
            """

            kwargs = {}
            if client_ip is not None:
                kwargs["client_ip"] = client_ip
            if idle_duration is not None:
                kwargs["idle_duration"] = idle_duration
            if local_request_count is not None:
                kwargs["local_request_count"] = local_request_count
            if protocol is not None:
                kwargs["protocol"] = protocol
            if remote_request_count is not None:
                kwargs["remote_request_count"] = remote_request_count
            if server_ip is not None:
                kwargs["server_ip"] = server_ip
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return NfsClients.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NfsClients resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the NFS configuration of SVMs.
### Expensive properties
export_policy.id is expensive field. It is not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `export_policy.id`

### Learn more
* [`DOC /protocols/nfs/connected-clients`](#docs-NAS-protocols_nfs_connected-clients)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)






