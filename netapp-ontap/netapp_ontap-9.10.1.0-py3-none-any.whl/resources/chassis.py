r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
You can use the chassis GET API to retrieve all of the chassis information in the cluster.
<br/>
## Examples
### Retrieving a list of chassis from the cluster
The following example shows the response with a list of chassis in the cluster:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Chassis

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(Chassis.get_collection()))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[Chassis({"id": "021352005981"})]

```
</div>
</div>

---
### Retrieving a specific chassis from the cluster
The following example shows the response of the requested chassis. If there is no chassis with the requested ID, an error is returned.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Chassis

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Chassis(id=21352005981)
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
Chassis(
    {
        "nodes": [
            {
                "uuid": "6ede364b-c3d0-11e8-a86a-00a098567f31",
                "position": "top",
                "pcis": {
                    "cards": [
                        {
                            "info": "\t  e0M MAC Address:    d0:39:ea:3f:06:2b (auto-1000t-fd-up) \n\t  e0S MAC Address:    d0:39:ea:3f:06:2c (auto-1000t-fd-up) \n\t  Device Type:        1533\n\t  Firmware Version:   3.25-0.0 0x800005D1\n",
                            "device": "Gigabit Ethernet I210",
                            "slot": "0",
                        },
                        {
                            "info": "\t  Additional Info: 0 (0xaaf00000)   \n\t  SHM2S86Q120GLM22NP FW1146 114473MB 512B/sect (SPG190108HJ)  \n",
                            "device": "Intel Lewisburg series chipset SATA Controller",
                            "slot": "0",
                        },
                    ]
                },
                "usbs": {
                    "ports": [{"connected": False}],
                    "supported": True,
                    "enabled": True,
                },
                "name": "node-1",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/6ede364b-c3d0-11e8-a86a-00a098567f31"
                    }
                },
            }
        ],
        "id": "021352005981",
        "state": "ok",
        "frus": [
            {"type": "psu", "state": "ok", "id": "PSU2"},
            {"type": "psu", "state": "ok", "id": "PSU1"},
            {"type": "fan", "state": "ok", "id": "Fan2"},
            {"type": "fan", "state": "ok", "id": "Fan3"},
            {"type": "fan", "state": "ok", "id": "Fan1"},
        ],
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


__all__ = ["Chassis", "ChassisSchema"]
__pdoc__ = {
    "ChassisSchema.resource": False,
    "Chassis.chassis_show": False,
    "Chassis.chassis_create": False,
    "Chassis.chassis_modify": False,
    "Chassis.chassis_delete": False,
}


class ChassisSchema(ResourceSchema):
    """The fields of the Chassis object"""

    frus = fields.List(fields.Nested("netapp_ontap.models.chassis_frus.ChassisFrusSchema", unknown=EXCLUDE), data_key="frus")
    r""" List of FRUs in the chassis. """

    id = fields.Str(
        data_key="id",
    )
    r""" The id field of the chassis.

Example: 2.1352005981E10 """

    nodes = fields.List(fields.Nested("netapp_ontap.models.chassis_node.ChassisNodeSchema", unknown=EXCLUDE), data_key="nodes")
    r""" List of nodes in the chassis. """

    shelves = fields.List(fields.Nested("netapp_ontap.resources.shelf.ShelfSchema", unknown=EXCLUDE), data_key="shelves")
    r""" List of shelves in chassis. """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['ok', 'error']),
    )
    r""" The state field of the chassis.

Valid choices:

* ok
* error """

    @property
    def resource(self):
        return Chassis

    gettable_fields = [
        "frus",
        "id",
        "nodes",
        "shelves",
        "state",
    ]
    """frus,id,nodes,shelves,state,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Chassis.get_collection(fields=field)]
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
            raise NetAppRestError("Chassis modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Chassis(Resource):
    """Allows interaction with Chassis objects on the host"""

    _schema = ChassisSchema
    _path = "/api/cluster/chassis"
    _keys = ["id"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of chassis.
### Related ONTAP commands
* `system chassis show`
* `system chassis fru show`
### Learn more
* [`DOC /cluster/chassis`](#docs-cluster-cluster_chassis)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="chassis show")
        def chassis_show(
            fields: List[Choices.define(["id", "state", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of Chassis resources

            Args:
                id: 
                state: 
            """

            kwargs = {}
            if id is not None:
                kwargs["id"] = id
            if state is not None:
                kwargs["state"] = state
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return Chassis.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Chassis resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of chassis.
### Related ONTAP commands
* `system chassis show`
* `system chassis fru show`
### Learn more
* [`DOC /cluster/chassis`](#docs-cluster-cluster_chassis)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific chassis.
### Related ONTAP commands
* `system chassis show`
* `system chassis fru show`
### Learn more
* [`DOC /cluster/chassis`](#docs-cluster-cluster_chassis)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)





