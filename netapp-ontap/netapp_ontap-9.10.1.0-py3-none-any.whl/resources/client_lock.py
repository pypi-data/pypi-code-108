r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
A lock is a synchronization mechanism for enforcing limits on concurrent access to files where many clients can be
accessing the same file at the same time. Locks can be viewed or broken according to a wide range of query fields
that are presented in the lock information definition.<br/>
It is recommended that you provide as many fields as possible to optimize query processing.
## Examples
### Retrieving locks with all fields for all SVMs
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClientLock

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(ClientLock.get_collection(return_timeout=15, fields="*")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    ClientLock(
        {
            "share_lock": {"soft": False, "mode": "read_write_deny_write_delete"},
            "type": "share_level",
            "interface": {
                "ip": {"address": "10.140.115.95"},
                "uuid": "6bf26e25-9ae4-11eb-8597-0050568ec154",
                "name": "vs1.data",
            },
            "constituent": False,
            "owner_id": "feff-0206000000020000000204000000000000000000000000ffff0a4a07161053010001000000030000006c00000000000000",
            "client_address": "10.74.7.22",
            "svm": {"uuid": "5b4b6847-9ae4-11eb-8597-0050568ec154", "name": "vs1"},
            "uuid": "bf03d8b4-e145-498a-902d-b9fe5d546d18",
            "protocol": "cifs",
            "volume": {
                "uuid": "429dcc79-9af2-11eb-b313-0050568ec154",
                "name": "test_vol1",
            },
            "state": "granted",
            "smb": {
                "connect_state": "connected",
                "open_type": "durable",
                "open_group_id": "71756e2325a7eb11843f005056a4731c101068450bcdffff1c2c000000000000",
            },
            "node": {
                "uuid": "1f29b875-9ae3-11eb-8597-0050568ec154",
                "name": "bshalini-vsim3",
            },
            "path": "/test_vol1/Demo406.TXT",
        }
    ),
    ClientLock(
        {
            "type": "op_lock",
            "oplock_level": "batch",
            "interface": {
                "ip": {"address": "10.140.115.95"},
                "uuid": "6bf26e25-9ae4-11eb-8597-0050568ec154",
                "name": "vs1.data",
            },
            "constituent": False,
            "owner_id": "feff-0206000000020000000204000000000000000000000000ffff0a4a07161053010001000000030000006c00000000000000",
            "client_address": "10.74.7.22",
            "svm": {"uuid": "5b4b6847-9ae4-11eb-8597-0050568ec154", "name": "vs1"},
            "uuid": "0c33d18d-dcbc-492a-81b3-4c5740c46172",
            "protocol": "cifs",
            "volume": {
                "uuid": "429dcc79-9af2-11eb-b313-0050568ec154",
                "name": "test_vol1",
            },
            "state": "granted",
            "smb": {
                "connect_state": "connected",
                "open_group_id": "71756e2325a7eb11843f005056a4731c101068450bcdffff1c2c000000000000",
            },
            "node": {
                "uuid": "1f29b875-9ae3-11eb-8597-0050568ec154",
                "name": "bshalini-vsim3",
            },
            "path": "/test_vol1/Demo406.TXT",
        }
    ),
]

```
</div>
</div>

---
### Retrieving locks of a specific volume
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClientLock

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            ClientLock.get_collection(
                return_timeout=15,
                fields="*",
                **{"volume.uuid": "429dcc79-9af2-11eb-b313-0050568ec154"}
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
    ClientLock(
        {
            "interface": {
                "uuid": "6bf26e25-9ae4-11eb-8597-0050568ec154",
                "name": "vs1.data",
            },
            "svm": {"uuid": "5b4b6847-9ae4-11eb-8597-0050568ec154", "name": "vs1"},
            "uuid": "be1cdf00-37f1-4477-b6d0-bba8c4fa8c67",
            "volume": {
                "uuid": "429dcc79-9af2-11eb-b313-0050568ec154",
                "name": "test_vol1",
            },
            "path": "/test_vol1/Demo408.TXT",
        }
    ),
    ClientLock(
        {
            "interface": {
                "uuid": "6bf26e25-9ae4-11eb-8597-0050568ec154",
                "name": "vs1.data",
            },
            "svm": {"uuid": "5b4b6847-9ae4-11eb-8597-0050568ec154", "name": "vs1"},
            "uuid": "393cc06e-8b37-4f49-b09a-74d1eef79368",
            "volume": {
                "uuid": "429dcc79-9af2-11eb-b313-0050568ec154",
                "name": "test_vol1",
            },
            "path": "/test_vol1/Demo408.TXT",
        }
    ),
]

```
</div>
</div>

---
### Retrieving the lock for a specific UUID
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClientLock

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClientLock(uuid="be1cdf00-37f1-4477-b6d0-bba8c4fa8c67")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
ClientLock(
    {
        "share_lock": {"soft": False, "mode": "read_write_deny_write_delete"},
        "type": "share_level",
        "interface": {
            "ip": {"address": "10.140.115.95"},
            "uuid": "6bf26e25-9ae4-11eb-8597-0050568ec154",
            "name": "vs1.data",
        },
        "constituent": False,
        "owner_id": "feff-0206000000020000000204000000000000000000000000ffff0a4a07161053010001000000030000006c00000000000000",
        "client_address": "10.74.7.22",
        "svm": {"uuid": "5b4b6847-9ae4-11eb-8597-0050568ec154", "name": "vs1"},
        "uuid": "be1cdf00-37f1-4477-b6d0-bba8c4fa8c67",
        "protocol": "cifs",
        "volume": {"uuid": "429dcc79-9af2-11eb-b313-0050568ec154", "name": "test_vol1"},
        "state": "granted",
        "smb": {
            "connect_state": "connected",
            "open_type": "durable",
            "open_group_id": "71756e2325a7eb11843f005056a4731c101068450bcdffff1c2c000000000000",
        },
        "node": {
            "uuid": "1f29b875-9ae3-11eb-8597-0050568ec154",
            "name": "bshalini-vsim3",
        },
        "path": "/test_vol1/Demo406.TXT",
    }
)

```
</div>
</div>

---
### Deleting the lock for a specific UUID
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClientLock

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClientLock(uuid="be1cdf00-37f1-4477-b6d0-bba8c4fa8c67")
    resource.delete()

```

---
### Deleting all locks for a specific protocol
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClientLock

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClientLock()
    resource.delete(protocol="cifs")

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


__all__ = ["ClientLock", "ClientLockSchema"]
__pdoc__ = {
    "ClientLockSchema.resource": False,
    "ClientLock.client_lock_show": False,
    "ClientLock.client_lock_create": False,
    "ClientLock.client_lock_modify": False,
    "ClientLock.client_lock_delete": False,
}


class ClientLockSchema(ResourceSchema):
    """The fields of the ClientLock object"""

    byte_lock = fields.Nested("netapp_ontap.models.byte_lock.ByteLockSchema", data_key="byte_lock", unknown=EXCLUDE)
    r""" The byte_lock field of the client_lock. """

    client_address = fields.Str(
        data_key="client_address",
    )
    r""" IP address of the client holding the lock.

Example: 0.0.0.0 """

    constituent = fields.Boolean(
        data_key="constituent",
    )
    r""" Indicate if volume is contituent or not. """

    delegation = fields.Str(
        data_key="delegation",
        validate=enum_validation(['read', 'write']),
    )
    r""" Type of delegation.

Valid choices:

* read
* write """

    interface = fields.Nested("netapp_ontap.resources.ip_interface.IpInterfaceSchema", data_key="interface", unknown=EXCLUDE)
    r""" The interface field of the client_lock. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the client_lock. """

    oplock_level = fields.Str(
        data_key="oplock_level",
        validate=enum_validation(['exclusive', 'level2', 'batch', 'null', 'read_batch']),
    )
    r""" The oplock level determines which operations the client may cache locally.

Valid choices:

* exclusive
* level2
* batch
* null
* read_batch """

    owner_id = fields.Str(
        data_key="owner_id",
    )
    r""" Owner ID. """

    path = fields.Str(
        data_key="path",
    )
    r""" Object path """

    protocol = fields.Str(
        data_key="protocol",
        validate=enum_validation(['cifs', 'fcache', 'nfsv4', 'http', 'nlm', 'nfsv4.1', 'crposix']),
    )
    r""" Type of lock protocol.

Valid choices:

* cifs
* fcache
* nfsv4
* http
* nlm
* nfsv4.1
* crposix """

    share_lock = fields.Nested("netapp_ontap.models.share_lock.ShareLockSchema", data_key="share_lock", unknown=EXCLUDE)
    r""" The share_lock field of the client_lock. """

    smb = fields.Nested("netapp_ontap.models.smb.SmbSchema", data_key="smb", unknown=EXCLUDE)
    r""" The smb field of the client_lock. """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['granted', 'revoking', 'adjusted', 'denied', 'subsumed', 'gone', 'unused', 'waiting', 'timeout']),
    )
    r""" State of lock.

Valid choices:

* granted
* revoking
* adjusted
* denied
* subsumed
* gone
* unused
* waiting
* timeout """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the client_lock. """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['byte_range', 'share_level', 'op_lock', 'delegation']),
    )
    r""" Type of lock.

Valid choices:

* byte_range
* share_level
* op_lock
* delegation """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" Lock UUID

Example: ceeac1b4-8646-4c76-a054-1c96e87594aa """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the client_lock. """

    @property
    def resource(self):
        return ClientLock

    gettable_fields = [
        "byte_lock",
        "client_address",
        "constituent",
        "delegation",
        "interface.links",
        "interface.ip",
        "interface.name",
        "interface.uuid",
        "node.links",
        "node.name",
        "node.uuid",
        "oplock_level",
        "owner_id",
        "path",
        "protocol",
        "share_lock",
        "smb",
        "state",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "type",
        "uuid",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """byte_lock,client_address,constituent,delegation,interface.links,interface.ip,interface.name,interface.uuid,node.links,node.name,node.uuid,oplock_level,owner_id,path,protocol,share_lock,smb,state,svm.links,svm.name,svm.uuid,type,uuid,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "byte_lock",
        "client_address",
        "interface.ip",
        "interface.name",
        "interface.uuid",
        "node.name",
        "node.uuid",
        "path",
        "protocol",
        "share_lock",
        "smb",
        "svm.name",
        "svm.uuid",
        "uuid",
        "volume.name",
        "volume.uuid",
    ]
    """byte_lock,client_address,interface.ip,interface.name,interface.uuid,node.name,node.uuid,path,protocol,share_lock,smb,svm.name,svm.uuid,uuid,volume.name,volume.uuid,"""

    postable_fields = [
        "byte_lock",
        "client_address",
        "interface.ip",
        "interface.name",
        "interface.uuid",
        "node.name",
        "node.uuid",
        "path",
        "protocol",
        "share_lock",
        "smb",
        "svm.name",
        "svm.uuid",
        "uuid",
        "volume.name",
        "volume.uuid",
    ]
    """byte_lock,client_address,interface.ip,interface.name,interface.uuid,node.name,node.uuid,path,protocol,share_lock,smb,svm.name,svm.uuid,uuid,volume.name,volume.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in ClientLock.get_collection(fields=field)]
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
            raise NetAppRestError("ClientLock modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class ClientLock(Resource):
    r""" This object represents locks on a volume. """

    _schema = ClientLockSchema
    _path = "/api/protocols/locks"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves locks details.
### Related ONTAP commands
* `vserver locks  show`

### Learn more
* [`DOC /protocols/locks`](#docs-NAS-protocols_locks)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="client lock show")
        def client_lock_show(
            fields: List[Choices.define(["client_address", "constituent", "delegation", "oplock_level", "owner_id", "path", "protocol", "state", "type", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of ClientLock resources

            Args:
                client_address: IP address of the client holding the lock.
                constituent: Indicate if volume is contituent or not.
                delegation: Type of delegation.
                oplock_level: The oplock level determines which operations the client may cache locally.
                owner_id: Owner ID.
                path: Object path
                protocol: Type of lock protocol.
                state: State of lock.
                type: Type of lock.
                uuid: Lock UUID
            """

            kwargs = {}
            if client_address is not None:
                kwargs["client_address"] = client_address
            if constituent is not None:
                kwargs["constituent"] = constituent
            if delegation is not None:
                kwargs["delegation"] = delegation
            if oplock_level is not None:
                kwargs["oplock_level"] = oplock_level
            if owner_id is not None:
                kwargs["owner_id"] = owner_id
            if path is not None:
                kwargs["path"] = path
            if protocol is not None:
                kwargs["protocol"] = protocol
            if state is not None:
                kwargs["state"] = state
            if type is not None:
                kwargs["type"] = type
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return ClientLock.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all ClientLock resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)



    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["ClientLock"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes locks of given parameter.
### Related ONTAP commands
* `vserver locks break`

### Learn more
* [`DOC /protocols/locks`](#docs-NAS-protocols_locks)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves locks details.
### Related ONTAP commands
* `vserver locks  show`

### Learn more
* [`DOC /protocols/locks`](#docs-NAS-protocols_locks)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the lock for a specific UUID.
### Related ONTAP commands
* `vserver locks show`

### Learn more
* [`DOC /protocols/locks`](#docs-NAS-protocols_locks)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)



    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes locks of given parameter.
### Related ONTAP commands
* `vserver locks break`

### Learn more
* [`DOC /protocols/locks`](#docs-NAS-protocols_locks)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="client lock delete")
        async def client_lock_delete(
        ) -> None:
            """Delete an instance of a ClientLock resource

            Args:
                client_address: IP address of the client holding the lock.
                constituent: Indicate if volume is contituent or not.
                delegation: Type of delegation.
                oplock_level: The oplock level determines which operations the client may cache locally.
                owner_id: Owner ID.
                path: Object path
                protocol: Type of lock protocol.
                state: State of lock.
                type: Type of lock.
                uuid: Lock UUID
            """

            kwargs = {}
            if client_address is not None:
                kwargs["client_address"] = client_address
            if constituent is not None:
                kwargs["constituent"] = constituent
            if delegation is not None:
                kwargs["delegation"] = delegation
            if oplock_level is not None:
                kwargs["oplock_level"] = oplock_level
            if owner_id is not None:
                kwargs["owner_id"] = owner_id
            if path is not None:
                kwargs["path"] = path
            if protocol is not None:
                kwargs["protocol"] = protocol
            if state is not None:
                kwargs["state"] = state
            if type is not None:
                kwargs["type"] = type
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(ClientLock, "find"):
                resource = ClientLock.find(
                    **kwargs
                )
            else:
                resource = ClientLock()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete ClientLock: %s" % err)


