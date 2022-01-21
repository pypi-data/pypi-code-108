r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Retrieving storage tape information
The storage tape GET API retrieves all of the tapes in the cluster.
<br/>
---
## Examples
### 1) Retrieving a list of tapes from the cluster
#### The following example returns the list of tapes in the cluster:
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import TapeDevice

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(TapeDevice.get_collection()))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    TapeDevice(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/4083be52-5315-11eb-a839-00a0985ebbe7"
                    }
                },
                "uuid": "4083be52-5315-11eb-a839-00a0985ebbe7",
                "name": "st-8020-1-01",
            },
            "device_id": "2d.0",
        }
    ),
    TapeDevice(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/4083be52-5315-11eb-a839-00a0985ebbe7"
                    }
                },
                "uuid": "4083be52-5315-11eb-a839-00a0985ebbe7",
                "name": "st-8020-1-01",
            },
            "device_id": "2d.0L1",
        }
    ),
    TapeDevice(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/4083be52-5315-11eb-a839-00a0985ebbe7"
                    }
                },
                "uuid": "4083be52-5315-11eb-a839-00a0985ebbe7",
                "name": "st-8020-1-01",
            },
            "device_id": "qeg-tape-brocade2-8g:0.126",
        }
    ),
    TapeDevice(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/4083be52-5315-11eb-a839-00a0985ebbe7"
                    }
                },
                "uuid": "4083be52-5315-11eb-a839-00a0985ebbe7",
                "name": "st-8020-1-01",
            },
            "device_id": "stsw-broc6510-01:11.126",
        }
    ),
    TapeDevice(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/4083be52-5315-11eb-a839-00a0985ebbe7"
                    }
                },
                "uuid": "4083be52-5315-11eb-a839-00a0985ebbe7",
                "name": "st-8020-1-01",
            },
            "device_id": "stsw-broc6510-01:15.126",
        }
    ),
    TapeDevice(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/4083be52-5315-11eb-a839-00a0985ebbe7"
                    }
                },
                "uuid": "4083be52-5315-11eb-a839-00a0985ebbe7",
                "name": "st-8020-1-01",
            },
            "device_id": "stsw-broc6510-01:15.126L1",
        }
    ),
    TapeDevice(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/4083be52-5315-11eb-a839-00a0985ebbe7"
                    }
                },
                "uuid": "4083be52-5315-11eb-a839-00a0985ebbe7",
                "name": "st-8020-1-01",
            },
            "device_id": "stsw-broc6510-01:22.126",
        }
    ),
    TapeDevice(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/4083be52-5315-11eb-a839-00a0985ebbe7"
                    }
                },
                "uuid": "4083be52-5315-11eb-a839-00a0985ebbe7",
                "name": "st-8020-1-01",
            },
            "device_id": "stsw-broc6510-01:23.126",
        }
    ),
]

```
</div>
</div>

---
### 2) Retrieving a specific tape device from the cluster
#### The following example returns the requested tape device. If there is no tape with the requested UID, an error is returned.
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import TapeDevice

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = TapeDevice(
        device_id="2d.0", **{"node.uuid": "5f5275eb-5315-11eb-8ac4-00a0985e0dcf"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
TapeDevice(
    {
        "wwnn": "5001697722ee0010",
        "block_number": -1,
        "residual_count": 0,
        "type": "tape",
        "device_names": [
            {
                "no_rewind_device": "nrst0l",
                "rewind_device": "rst0l",
                "unload_reload_device": "urst0l",
            },
            {
                "no_rewind_device": "nrst0m",
                "rewind_device": "rst0m",
                "unload_reload_device": "urst0m",
            },
            {
                "no_rewind_device": "nrst0h",
                "rewind_device": "rst0h",
                "unload_reload_device": "urst0h",
            },
            {
                "no_rewind_device": "nrst0a",
                "rewind_device": "rst0a",
                "unload_reload_device": "urst0a",
            },
        ],
        "interface": "sas",
        "node": {
            "_links": {
                "self": {
                    "href": "/api/cluster/nodes/5f5275eb-5315-11eb-8ac4-00a0985e0dcf"
                }
            },
            "uuid": "5f5275eb-5315-11eb-8ac4-00a0985e0dcf",
            "name": "st-8020-1-02",
        },
        "device_id": "2d.0",
        "file_number": -1,
        "formats": [
            "LTO-4/5 Native Density",
            "LTO-4/5 Compressed",
            "LTO-6 2.5TB",
            "LTO-6 6.25TB Compressed",
        ],
        "wwpn": "5001697722ee0011",
        "reservation_type": "off",
        "device_state": "offline",
        "storage_port": {"name": "2d"},
        "description": "IBM LTO-6 ULT3580",
        "serial_number": "1068000245",
        "alias": {"mapping": "SN[1068000245]", "name": "st7"},
    }
)

```
</div>
</div>

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


__all__ = ["TapeDevice", "TapeDeviceSchema"]
__pdoc__ = {
    "TapeDeviceSchema.resource": False,
    "TapeDevice.tape_device_show": False,
    "TapeDevice.tape_device_create": False,
    "TapeDevice.tape_device_modify": False,
    "TapeDevice.tape_device_delete": False,
}


class TapeDeviceSchema(ResourceSchema):
    """The fields of the TapeDevice object"""

    alias = fields.Nested("netapp_ontap.models.tape_device_alias.TapeDeviceAliasSchema", data_key="alias", unknown=EXCLUDE)
    r""" The alias field of the tape_device. """

    block_number = Size(
        data_key="block_number",
    )
    r""" Block number.

Example: 0 """

    description = fields.Str(
        data_key="description",
    )
    r""" The description field of the tape_device.

Example: QUANTUM LTO-8 ULTRIUM """

    device_id = fields.Str(
        data_key="device_id",
    )
    r""" The device_id field of the tape_device.

Example: 1a.0 """

    device_names = fields.List(fields.Nested("netapp_ontap.models.tape_device_device_names.TapeDeviceDeviceNamesSchema", unknown=EXCLUDE), data_key="device_names")
    r""" The device_names field of the tape_device. """

    device_state = fields.Str(
        data_key="device_state",
        validate=enum_validation(['unknown', 'available', 'ready_write_enabled', 'ready_write_protected', 'offline', 'in_use', 'error', 'reserved_by_another_host', 'normal', 'rewinding', 'erasing']),
    )
    r""" Operational state of the device.

Valid choices:

* unknown
* available
* ready_write_enabled
* ready_write_protected
* offline
* in_use
* error
* reserved_by_another_host
* normal
* rewinding
* erasing """

    file_number = Size(
        data_key="file_number",
    )
    r""" File number.

Example: 0 """

    formats = fields.List(fields.Str, data_key="formats")
    r""" Tape cartridge format.

Example: ["LTO-7 6TB","LTO-7 15TB Compressed","LTO-8 12TB","LTO-8 30TB Compressed"] """

    interface = fields.Str(
        data_key="interface",
        validate=enum_validation(['unknown', 'fibre_channel', 'sas', 'pscsi']),
    )
    r""" Device interface type.

Valid choices:

* unknown
* fibre_channel
* sas
* pscsi """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the tape_device. """

    reservation_type = fields.Str(
        data_key="reservation_type",
        validate=enum_validation(['off', 'persistent', 'scsi']),
    )
    r""" The reservation_type field of the tape_device.

Valid choices:

* off
* persistent
* scsi """

    residual_count = Size(
        data_key="residual_count",
    )
    r""" Residual count of the last I/O operation.

Example: 0 """

    serial_number = fields.Str(
        data_key="serial_number",
    )
    r""" The serial_number field of the tape_device.

Example: 10WT00093 """

    storage_port = fields.Nested("netapp_ontap.models.tape_device_storage_port.TapeDeviceStoragePortSchema", data_key="storage_port", unknown=EXCLUDE)
    r""" The storage_port field of the tape_device. """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['unknown', 'tape', 'media_changer']),
    )
    r""" Device type.

Valid choices:

* unknown
* tape
* media_changer """

    wwnn = fields.Str(
        data_key="wwnn",
    )
    r""" World Wide Node Name.

Example: 500507631295741c """

    wwpn = fields.Str(
        data_key="wwpn",
    )
    r""" World Wide Port Name.

Example: 500507631295741c """

    @property
    def resource(self):
        return TapeDevice

    gettable_fields = [
        "alias",
        "block_number",
        "description",
        "device_id",
        "device_names",
        "device_state",
        "file_number",
        "formats",
        "interface",
        "node.links",
        "node.name",
        "node.uuid",
        "reservation_type",
        "residual_count",
        "serial_number",
        "storage_port",
        "type",
        "wwnn",
        "wwpn",
    ]
    """alias,block_number,description,device_id,device_names,device_state,file_number,formats,interface,node.links,node.name,node.uuid,reservation_type,residual_count,serial_number,storage_port,type,wwnn,wwpn,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in TapeDevice.get_collection(fields=field)]
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
            raise NetAppRestError("TapeDevice modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class TapeDevice(Resource):
    """Allows interaction with TapeDevice objects on the host"""

    _schema = TapeDeviceSchema
    _path = "/api/storage/tape-devices"
    _keys = ["node.uuid", "device_id"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of tape devices.
### Related ONTAP commands
* `storage tape show`
### Learn more
* [`DOC /storage/tape-devices`](#docs-storage-storage_tape-devices)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="tape device show")
        def tape_device_show(
            fields: List[Choices.define(["block_number", "description", "device_id", "device_state", "file_number", "formats", "interface", "reservation_type", "residual_count", "serial_number", "type", "wwnn", "wwpn", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of TapeDevice resources

            Args:
                block_number: Block number.
                description: 
                device_id: 
                device_state: Operational state of the device.
                file_number: File number.
                formats: Tape cartridge format.
                interface: Device interface type.
                reservation_type: 
                residual_count: Residual count of the last I/O operation.
                serial_number: 
                type: Device type.
                wwnn: World Wide Node Name.
                wwpn: World Wide Port Name.
            """

            kwargs = {}
            if block_number is not None:
                kwargs["block_number"] = block_number
            if description is not None:
                kwargs["description"] = description
            if device_id is not None:
                kwargs["device_id"] = device_id
            if device_state is not None:
                kwargs["device_state"] = device_state
            if file_number is not None:
                kwargs["file_number"] = file_number
            if formats is not None:
                kwargs["formats"] = formats
            if interface is not None:
                kwargs["interface"] = interface
            if reservation_type is not None:
                kwargs["reservation_type"] = reservation_type
            if residual_count is not None:
                kwargs["residual_count"] = residual_count
            if serial_number is not None:
                kwargs["serial_number"] = serial_number
            if type is not None:
                kwargs["type"] = type
            if wwnn is not None:
                kwargs["wwnn"] = wwnn
            if wwpn is not None:
                kwargs["wwpn"] = wwpn
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return TapeDevice.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all TapeDevice resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of tape devices.
### Related ONTAP commands
* `storage tape show`
### Learn more
* [`DOC /storage/tape-devices`](#docs-storage-storage_tape-devices)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific tape.
### Related ONTAP commands
* `storage tape show`
### Learn more
* [`DOC /storage/tape-devices`](#docs-storage-storage_tape-devices)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)





