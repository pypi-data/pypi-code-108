r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
This API is used to display and update connection status information for external FPolicy servers.
You must keep the following in mind while using these endpoints:

* If the passthrough_read field is set to true in a GET collection call, only Fpolicy passthrough-read connections are returned.
* If the passthrough_read field is not provided or set to false in a GET collection call, only FPolicy server connections are returned.
## Examples
### Retrieving the FPolicy server connections for all SVMs in the cluster
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyConnection

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(FpolicyConnection.get_collection("*", passthrough_read=False, fields="*"))
    )

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    FpolicyConnection(
        {
            "type": "primary",
            "disconnected_reason": {
                "code": 9305,
                "message": "No local lif present to connect to FPolicy server.",
            },
            "svm": {"uuid": "9f738ac5-c502-11eb-b82c-0050568e5902", "name": "vs1"},
            "policy": {"name": "p1"},
            "server": "192.168.137.78",
            "state": "disconnected",
            "update_time": "2021-06-17T16:05:15+05:30",
            "node": {
                "uuid": "8ca36b68-c501-11eb-b82c-0050568e5902",
                "name": "hsaraswa-vsim4",
            },
        }
    ),
    FpolicyConnection(
        {
            "type": "primary",
            "disconnected_reason": {
                "code": 9305,
                "message": "No local lif present to connect to FPolicy server.",
            },
            "svm": {"uuid": "9f738ac5-c502-11eb-b82c-0050568e5902", "name": "vs1"},
            "policy": {"name": "p2"},
            "server": "192.168.136.38",
            "state": "disconnected",
            "update_time": "2021-06-17T16:05:15+05:30",
            "node": {
                "uuid": "8ca36b68-c501-11eb-b82c-0050568e5902",
                "name": "hsaraswa-vsim4",
            },
        }
    ),
    FpolicyConnection(
        {
            "type": "primary",
            "disconnected_reason": {
                "code": 9305,
                "message": "No local lif present to connect to FPolicy server.",
            },
            "svm": {"uuid": "b6df362b-c502-11eb-b82c-0050568e5902", "name": "vs2"},
            "policy": {"name": "pol1"},
            "server": "192.168.129.146",
            "state": "disconnected",
            "update_time": "2021-06-17T16:05:15+05:30",
            "node": {
                "uuid": "8ca36b68-c501-11eb-b82c-0050568e5902",
                "name": "hsaraswa-vsim4",
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving all FPolicy passthrough read connections for all SVMs in the cluster
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyConnection

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            FpolicyConnection.get_collection(
                "*", passthrough_read=True, fields="*", return_timeout=15
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
    FpolicyConnection(
        {
            "session_uuid": "2410d348-c7cb-11eb-a07a-0050568ebc01",
            "svm": {"uuid": "a69e938d-c7ca-11eb-a07a-0050568ebc01", "name": "vs2"},
            "policy": {"name": "pol1"},
            "server": "192.168.129.146",
            "state": "connected",
            "node": {
                "uuid": "55693090-c7c8-11eb-a07a-0050568ebc01",
                "name": "chiragm-vsim3",
            },
        }
    ),
    FpolicyConnection(
        {
            "session_uuid": "288f7002-c7cb-11eb-a07a-0050568ebc01",
            "svm": {"uuid": "a69e938d-c7ca-11eb-a07a-0050568ebc01", "name": "vs2"},
            "policy": {"name": "pol2"},
            "server": "192.168.129.146",
            "state": "connected",
            "node": {
                "uuid": "55693090-c7c8-11eb-a07a-0050568ebc01",
                "name": "chiragm-vsim3",
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving the FPolicy server connections for a specific SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyConnection

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            FpolicyConnection.get_collection(
                "9f738ac5-c502-11eb-b82c-0050568e5902",
                passthrough_read=False,
                fields="*",
            )
        )
    )

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    FpolicyConnection(
        {
            "type": "primary",
            "disconnected_reason": {
                "code": 9305,
                "message": "No local lif present to connect to FPolicy server.",
            },
            "svm": {"uuid": "9f738ac5-c502-11eb-b82c-0050568e5902", "name": "vs1"},
            "policy": {"name": "p1"},
            "server": "192.168.137.78",
            "state": "disconnected",
            "update_time": "2021-06-17T16:05:15+05:30",
            "node": {
                "uuid": "8ca36b68-c501-11eb-b82c-0050568e5902",
                "name": "hsaraswa-vsim4",
            },
        }
    ),
    FpolicyConnection(
        {
            "type": "primary",
            "disconnected_reason": {
                "code": 9305,
                "message": "No local lif present to connect to FPolicy server.",
            },
            "svm": {"uuid": "9f738ac5-c502-11eb-b82c-0050568e5902", "name": "vs1"},
            "policy": {"name": "p2"},
            "server": "192.168.136.38",
            "state": "disconnected",
            "update_time": "2021-06-17T16:05:15+05:30",
            "node": {
                "uuid": "8ca36b68-c501-11eb-b82c-0050568e5902",
                "name": "hsaraswa-vsim4",
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving a specific FPolicy server connection
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyConnection

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyConnection(
        "9f738ac5-c502-11eb-b82c-0050568e5902",
        server="192.168.137.78",
        **{"policy.name": "p1", "node.uuid": "8ca36b68-c501-11eb-b82c-0050568e5902"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
FpolicyConnection(
    {
        "type": "primary",
        "disconnected_reason": {
            "code": 9305,
            "message": "No local lif present to connect to FPolicy server.",
        },
        "svm": {"uuid": "9f738ac5-c502-11eb-b82c-0050568e5902", "name": "vs1"},
        "policy": {"name": "p1"},
        "server": "192.168.137.78",
        "state": "disconnected",
        "update_time": "2021-06-17T16:05:15+05:30",
        "node": {
            "uuid": "8ca36b68-c501-11eb-b82c-0050568e5902",
            "name": "hsaraswa-vsim4",
        },
    }
)

```
</div>
</div>

---
### Updating the FPolicy server connection
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyConnection

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyConnection(
        "9f738ac5-c502-11eb-b82c-0050568e5902",
        server="192.168.137.78",
        **{"policy.name": "p1", "node.uuid": "8ca36b68-c501-11eb-b82c-0050568e5902"}
    )
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


__all__ = ["FpolicyConnection", "FpolicyConnectionSchema"]
__pdoc__ = {
    "FpolicyConnectionSchema.resource": False,
    "FpolicyConnection.fpolicy_connection_show": False,
    "FpolicyConnection.fpolicy_connection_create": False,
    "FpolicyConnection.fpolicy_connection_modify": False,
    "FpolicyConnection.fpolicy_connection_delete": False,
}


class FpolicyConnectionSchema(ResourceSchema):
    """The fields of the FpolicyConnection object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the fpolicy_connection. """

    disconnected_reason = fields.Nested("netapp_ontap.models.fpolicy_connection_disconnected_reason.FpolicyConnectionDisconnectedReasonSchema", data_key="disconnected_reason", unknown=EXCLUDE)
    r""" The disconnected_reason field of the fpolicy_connection. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the fpolicy_connection. """

    policy = fields.Nested("netapp_ontap.resources.fpolicy_policy.FpolicyPolicySchema", data_key="policy", unknown=EXCLUDE)
    r""" The policy field of the fpolicy_connection. """

    server = fields.Str(
        data_key="server",
    )
    r""" IP address of the FPolicy server.

Example: 10.132.145.20 """

    session_uuid = fields.Str(
        data_key="session_uuid",
    )
    r""" Unique session ID associated with each connection to the FPolicy server and it can be used to identify
the established connection.


Example: 5224ec64-b336-11eb-841c-0050568e14c2 """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['connected', 'disconnected']),
    )
    r""" Specifies the FPolicy server connection state indicating if it is in the connected or disconnected state.
The following is a list of the possible states:

* connected                 - Connected
* disconnected              - Disconnected


Valid choices:

* connected
* disconnected """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the fpolicy_connection. """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['primary', 'secondary']),
    )
    r""" FPolicy server type. The possible values are:

  * primary - Primary server
  * secondary  - Secondary server


Valid choices:

* primary
* secondary """

    update_time = ImpreciseDateTime(
        data_key="update_time",
    )
    r""" Specifies the time at which FPolicy server is connected or disconnected.

Example: 2019-06-12T15:00:16.000+0000 """

    @property
    def resource(self):
        return FpolicyConnection

    gettable_fields = [
        "links",
        "disconnected_reason",
        "node.links",
        "node.name",
        "node.uuid",
        "policy.links",
        "policy.name",
        "server",
        "session_uuid",
        "state",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "type",
        "update_time",
    ]
    """links,disconnected_reason,node.links,node.name,node.uuid,policy.links,policy.name,server,session_uuid,state,svm.links,svm.name,svm.uuid,type,update_time,"""

    patchable_fields = [
        "disconnected_reason",
        "node.name",
        "node.uuid",
        "state",
        "svm.name",
        "svm.uuid",
    ]
    """disconnected_reason,node.name,node.uuid,state,svm.name,svm.uuid,"""

    postable_fields = [
        "disconnected_reason",
        "node.name",
        "node.uuid",
        "state",
        "svm.name",
        "svm.uuid",
    ]
    """disconnected_reason,node.name,node.uuid,state,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FpolicyConnection.get_collection(fields=field)]
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
            raise NetAppRestError("FpolicyConnection modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FpolicyConnection(Resource):
    r""" Displays the connection status information of the FPolicy server. """

    _schema = FpolicyConnectionSchema
    _path = "/api/protocols/fpolicy/{svm[uuid]}/connections"
    _keys = ["svm.uuid", "node.uuid", "policy.name", "server"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the statuses of FPolicy servers.
### Related ONTAP commands
* `vserver fpolicy show-engine`
* `vserver fpolicy show-passthrough-read-connection`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/connections`](#docs-NAS-protocols_fpolicy_{svm.uuid}_connections)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fpolicy connection show")
        def fpolicy_connection_show(
            svm_uuid,
            server: Choices.define(_get_field_list("server"), cache_choices=True, inexact=True)=None,
            session_uuid: Choices.define(_get_field_list("session_uuid"), cache_choices=True, inexact=True)=None,
            state: Choices.define(_get_field_list("state"), cache_choices=True, inexact=True)=None,
            type: Choices.define(_get_field_list("type"), cache_choices=True, inexact=True)=None,
            update_time: Choices.define(_get_field_list("update_time"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["server", "session_uuid", "state", "type", "update_time", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of FpolicyConnection resources

            Args:
                server: IP address of the FPolicy server.
                session_uuid: Unique session ID associated with each connection to the FPolicy server and it can be used to identify the established connection. 
                state: Specifies the FPolicy server connection state indicating if it is in the connected or disconnected state. The following is a list of the possible states: * connected                 - Connected * disconnected              - Disconnected 
                type: FPolicy server type. The possible values are:   * primary - Primary server   * secondary  - Secondary server 
                update_time: Specifies the time at which FPolicy server is connected or disconnected.
            """

            kwargs = {}
            if server is not None:
                kwargs["server"] = server
            if session_uuid is not None:
                kwargs["session_uuid"] = session_uuid
            if state is not None:
                kwargs["state"] = state
            if type is not None:
                kwargs["type"] = type
            if update_time is not None:
                kwargs["update_time"] = update_time
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return FpolicyConnection.get_collection(
                svm_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all FpolicyConnection resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["FpolicyConnection"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the status of an FPolicy server.
### Related ONTAP commands
* `vserver fpolicy engine-connect`
* `vserver fpolicy engine-disconnect`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/connections`](#docs-NAS-protocols_fpolicy_{svm.uuid}_connections)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)



    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the statuses of FPolicy servers.
### Related ONTAP commands
* `vserver fpolicy show-engine`
* `vserver fpolicy show-passthrough-read-connection`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/connections`](#docs-NAS-protocols_fpolicy_{svm.uuid}_connections)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the status of an FPolicy server.
### Related ONTAP commands
* `vserver fpolicy show-engine`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/connections`](#docs-NAS-protocols_fpolicy_{svm.uuid}_connections)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)


    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the status of an FPolicy server.
### Related ONTAP commands
* `vserver fpolicy engine-connect`
* `vserver fpolicy engine-disconnect`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/connections`](#docs-NAS-protocols_fpolicy_{svm.uuid}_connections)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fpolicy connection modify")
        async def fpolicy_connection_modify(
            svm_uuid,
            server: str = None,
            query_server: str = None,
            session_uuid: str = None,
            query_session_uuid: str = None,
            state: str = None,
            query_state: str = None,
            type: str = None,
            query_type: str = None,
            update_time: datetime = None,
            query_update_time: datetime = None,
        ) -> ResourceTable:
            """Modify an instance of a FpolicyConnection resource

            Args:
                server: IP address of the FPolicy server.
                query_server: IP address of the FPolicy server.
                session_uuid: Unique session ID associated with each connection to the FPolicy server and it can be used to identify the established connection. 
                query_session_uuid: Unique session ID associated with each connection to the FPolicy server and it can be used to identify the established connection. 
                state: Specifies the FPolicy server connection state indicating if it is in the connected or disconnected state. The following is a list of the possible states: * connected                 - Connected * disconnected              - Disconnected 
                query_state: Specifies the FPolicy server connection state indicating if it is in the connected or disconnected state. The following is a list of the possible states: * connected                 - Connected * disconnected              - Disconnected 
                type: FPolicy server type. The possible values are:   * primary - Primary server   * secondary  - Secondary server 
                query_type: FPolicy server type. The possible values are:   * primary - Primary server   * secondary  - Secondary server 
                update_time: Specifies the time at which FPolicy server is connected or disconnected.
                query_update_time: Specifies the time at which FPolicy server is connected or disconnected.
            """

            kwargs = {}
            changes = {}
            if query_server is not None:
                kwargs["server"] = query_server
            if query_session_uuid is not None:
                kwargs["session_uuid"] = query_session_uuid
            if query_state is not None:
                kwargs["state"] = query_state
            if query_type is not None:
                kwargs["type"] = query_type
            if query_update_time is not None:
                kwargs["update_time"] = query_update_time

            if server is not None:
                changes["server"] = server
            if session_uuid is not None:
                changes["session_uuid"] = session_uuid
            if state is not None:
                changes["state"] = state
            if type is not None:
                changes["type"] = type
            if update_time is not None:
                changes["update_time"] = update_time

            if hasattr(FpolicyConnection, "find"):
                resource = FpolicyConnection.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = FpolicyConnection(svm_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify FpolicyConnection: %s" % err)



