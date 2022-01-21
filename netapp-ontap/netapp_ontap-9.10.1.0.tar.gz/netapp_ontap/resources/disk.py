r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Retrieving storage disk information
The storage disk GET API retrieves all of the disks in the cluster.
<br/>
---
## Examples
### 1) Retrieve a list of disks from the cluster.
#### The following example shows the response with a list of disks in the cluster:
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Disk

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(Disk.get_collection()))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    Disk({"name": "1.24.4"}),
    Disk({"name": "1.24.3"}),
    Disk({"name": "1.24.5"}),
    Disk({"name": "1.24.0"}),
    Disk({"name": "1.24.2"}),
    Disk({"name": "1.24.1"}),
]

```
</div>
</div>

---
### 2) Retrieve a specific disk from the cluster.
#### The following example shows the response of the requested disk. If there is no disk with the requested name, an error is returned:
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Disk

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Disk(name="1.24.3")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
Disk(
    {
        "usable_size": 438304768000,
        "home_node": {
            "_links": {
                "self": {
                    "href": "/api/cluster/nodes/3a89ed49-8c6d-11e8-93bc-00a0985a64b6"
                }
            },
            "uuid": "3a89ed49-8c6d-11e8-93bc-00a0985a64b6",
            "name": "node-2",
        },
        "local": True,
        "pool": "pool0",
        "bay": 3,
        "serial_number": "EC47PC5021SW",
        "vendor": "NETAPP",
        "state": "present",
        "outage": {
            "persistently_failed": True,
            "reason": {
                "code": "721081",
                "message": 'Failed disk. Reason: "admin failed".',
            },
        },
        "sector_count": 1172123568,
        "class": "performance",
        "firmware_version": "NA02",
        "error": [
            {
                "type": "notallflashdisk",
                "reason": {
                    "code": "721082",
                    "message": '"The node is configured with All-Flash Optimized personality and this disk is not an SSD. The disk needs to be removed from the system."',
                },
            }
        ],
        "model": "X421_FAL12450A10",
        "node": {
            "_links": {
                "self": {
                    "href": "/api/cluster/nodes/3a89ed49-8c6d-11e8-93bc-00a0985a64b6"
                }
            },
            "uuid": "3a89ed49-8c6d-11e8-93bc-00a0985a64b6",
            "name": "node-2",
        },
        "rpm": 10000,
        "type": "sas",
        "shelf": {"uid": "10318311901725526608"},
        "bytes_per_sector": 512,
        "paths": [
            {
                "port_type": "sas",
                "port_name": "B",
                "wwpn": "5000cca02f0e676a",
                "initiator": "3a",
                "wwnn": "5000cca02f0e6768",
            },
            {
                "port_type": "sas",
                "port_name": "A",
                "wwpn": "5000cca02f0e6769",
                "initiator": "3d",
                "wwnn": "5000cca02f0e6768",
            },
            {
                "port_type": "sas",
                "port_name": "A",
                "wwpn": "5000cca02f0e6769",
                "initiator": "3d",
                "wwnn": "5000cca02f0e6768",
            },
            {
                "port_type": "sas",
                "port_name": "B",
                "wwpn": "5000cca02f0e676a",
                "initiator": "3a",
                "wwnn": "5000cca02f0e6768",
            },
        ],
        "stats": {
            "throughput": 1957888,
            "power_on_hours": 11797,
            "path_error_count": 0,
            "average_latency": 6,
            "iops_total": 12854,
        },
        "effective_type": "sas",
        "container_type": "aggregate",
        "uid": "50000394:0808AA88:00000000:00000000:00000000:00000000:00000000:00000000:00000000:00000000",
        "aggregates": [
            {
                "name": "node_2_SAS_1",
                "uuid": "3fd9c345-ba91-4949-a7b1-6e2b898d74e3",
                "_links": {
                    "self": {
                        "href": "/api/storage/aggregates/3fd9c345-ba91-4949-a7b1-6e2b898d74e3"
                    }
                },
            }
        ],
        "name": "1.24.3",
    }
)

```
</div>
</div>

---
## Modifying storage disk
The storage disk PATCH API modifies disk ownership or encrypting drive authentication keys (AKs) in the cluster.
### Updating the disk ownership for a specified disk
### 1. When the disk is not assigned
When the disk is a spare (or unowned) disk and node name is specified, the PATCH opertaion assigns the disk to the specified node.
### 2. When the disk is already assigned
When the disk is already assigned (aleady has a owner), and a new node is specified, the PATCH operation changes the ownership to the new node.
<br/>
---
## Examples
### 1. Update the disk ownership for an unowned disk
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Disk

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Disk(name="<disk-name>")
    resource.node = {"name": "node-name"}
    resource.patch()

```

---
### 2. Update the disk ownership for an already owned disk.
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Disk

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Disk(name="<disk-name>")
    resource.node = {"name": "node-name"}
    resource.patch()

```

---
### 3. Rekey the data AK of all encrypting drives to an AK selected automatically by the system.
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Disk

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Disk()
    resource.patch(hydrate=True, name="*", encryption_operation="rekey_data_auto_id")

```

---
### 4. Cryptographically sanitize a spare or broken disk.
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Disk

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Disk()
    resource.patch(
        hydrate=True, name="<disk-name>", encryption_operation="sanitize_disk"
    )

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


__all__ = ["Disk", "DiskSchema"]
__pdoc__ = {
    "DiskSchema.resource": False,
    "Disk.disk_show": False,
    "Disk.disk_create": False,
    "Disk.disk_modify": False,
    "Disk.disk_delete": False,
}


class DiskSchema(ResourceSchema):
    """The fields of the Disk object"""

    aggregates = fields.List(fields.Nested("netapp_ontap.resources.aggregate.AggregateSchema", unknown=EXCLUDE), data_key="aggregates")
    r""" List of aggregates sharing this disk """

    bay = Size(
        data_key="bay",
    )
    r""" Disk shelf bay

Example: 1 """

    bytes_per_sector = Size(
        data_key="bytes_per_sector",
    )
    r""" Bytes per sector.

Example: 520 """

    class_ = fields.Str(
        data_key="class",
        validate=enum_validation(['unknown', 'capacity', 'performance', 'archive', 'solid_state', 'array', 'virtual']),
    )
    r""" Disk class

Valid choices:

* unknown
* capacity
* performance
* archive
* solid_state
* array
* virtual """

    container_type = fields.Str(
        data_key="container_type",
        validate=enum_validation(['aggregate', 'broken', 'foreign', 'labelmaint', 'maintenance', 'shared', 'spare', 'unassigned', 'unknown', 'unsupported', 'remote', 'mediator']),
    )
    r""" Type of overlying disk container

Valid choices:

* aggregate
* broken
* foreign
* labelmaint
* maintenance
* shared
* spare
* unassigned
* unknown
* unsupported
* remote
* mediator """

    dr_node = fields.Nested("netapp_ontap.models.dr_node.DrNodeSchema", data_key="dr_node", unknown=EXCLUDE)
    r""" The dr_node field of the disk. """

    drawer = fields.Nested("netapp_ontap.models.disk_drawer.DiskDrawerSchema", data_key="drawer", unknown=EXCLUDE)
    r""" The drawer field of the disk. """

    effective_type = fields.Str(
        data_key="effective_type",
        validate=enum_validation(['ata', 'fcal', 'lun', 'msata', 'sas', 'bsas', 'ssd', 'ssd_nvm', 'ssd_cap', 'fsas', 'vmdisk', 'unknown']),
    )
    r""" Effective Disk type

Valid choices:

* ata
* fcal
* lun
* msata
* sas
* bsas
* ssd
* ssd_nvm
* ssd_cap
* fsas
* vmdisk
* unknown """

    encryption_operation = fields.Str(
        data_key="encryption_operation",
    )
    r""" This field should only be set as a query parameter in a PATCH operation. It is input only and won't be returned by a subsequent GET. """

    error = fields.List(fields.Nested("netapp_ontap.models.disk_error_info.DiskErrorInfoSchema", unknown=EXCLUDE), data_key="error")
    r""" List of disk errors information. """

    fips_certified = fields.Boolean(
        data_key="fips_certified",
    )
    r""" The fips_certified field of the disk. """

    firmware_version = fields.Str(
        data_key="firmware_version",
    )
    r""" The firmware_version field of the disk.

Example: NA51 """

    home_node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="home_node", unknown=EXCLUDE)
    r""" The home_node field of the disk. """

    key_id = fields.Nested("netapp_ontap.models.disk_key_id.DiskKeyIdSchema", data_key="key_id", unknown=EXCLUDE)
    r""" The key_id field of the disk. """

    local = fields.Boolean(
        data_key="local",
    )
    r""" Indicates if a disk is locally attached versus being remotely attached.
A locally attached disk resides in the same proximity as the host
cluster versus been attached to the remote cluster. """

    model = fields.Str(
        data_key="model",
    )
    r""" The model field of the disk.

Example: X421_HCOBE450A10 """

    name = fields.Str(
        data_key="name",
    )
    r""" Cluster-wide disk name

Example: 1.0.1 """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the disk. """

    outage = fields.Nested("netapp_ontap.models.disk_outage.DiskOutageSchema", data_key="outage", unknown=EXCLUDE)
    r""" The outage field of the disk. """

    paths = fields.List(fields.Nested("netapp_ontap.models.disk_path_info.DiskPathInfoSchema", unknown=EXCLUDE), data_key="paths")
    r""" List of paths to a disk """

    pool = fields.Str(
        data_key="pool",
        validate=enum_validation(['pool0', 'pool1', 'failed', 'none']),
    )
    r""" Pool to which disk is assigned

Valid choices:

* pool0
* pool1
* failed
* none """

    protection_mode = fields.Str(
        data_key="protection_mode",
        validate=enum_validation(['open', 'data', 'part', 'full', 'miss']),
    )
    r""" Mode of drive data protection and FIPS compliance. Possible values are:
- _open_ - Data is unprotected
- _data_ - Data protection only, without FIPS compliance
- _part_ - Data is unprotected; other FIPS compliance settings present
- _full_ - Full data and FIPS compliance protection
- _miss_ - Protection mode information is not available


Valid choices:

* open
* data
* part
* full
* miss """

    rated_life_used_percent = Size(
        data_key="rated_life_used_percent",
    )
    r""" Percentage of rated life used

Example: 10 """

    rpm = Size(
        data_key="rpm",
    )
    r""" Revolutions per minute

Example: 15000 """

    sector_count = Size(
        data_key="sector_count",
    )
    r""" Number of sectors on the disk.

Example: 1172123568 """

    self_encrypting = fields.Boolean(
        data_key="self_encrypting",
    )
    r""" The self_encrypting field of the disk. """

    serial_number = fields.Str(
        data_key="serial_number",
    )
    r""" The serial_number field of the disk.

Example: KHG2VX8R """

    shelf = fields.Nested("netapp_ontap.resources.shelf.ShelfSchema", data_key="shelf", unknown=EXCLUDE)
    r""" The shelf field of the disk. """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['broken', 'copy', 'maintenance', 'partner', 'pending', 'present', 'reconstructing', 'removed', 'spare', 'unfail', 'zeroing']),
    )
    r""" State

Valid choices:

* broken
* copy
* maintenance
* partner
* pending
* present
* reconstructing
* removed
* spare
* unfail
* zeroing """

    stats = fields.Nested("netapp_ontap.models.disk_stats.DiskStatsSchema", data_key="stats", unknown=EXCLUDE)
    r""" The stats field of the disk. """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['ata', 'bsas', 'fcal', 'fsas', 'lun', 'sas', 'msata', 'ssd', 'vmdisk', 'unknown', 'ssd_cap', 'ssd_nvm', 'ssd_zns']),
    )
    r""" Disk interface type

Valid choices:

* ata
* bsas
* fcal
* fsas
* lun
* sas
* msata
* ssd
* vmdisk
* unknown
* ssd_cap
* ssd_nvm
* ssd_zns """

    uid = fields.Str(
        data_key="uid",
    )
    r""" The unique identifier for a disk

Example: 002538E5:71B00B2F:00000000:00000000:00000000:00000000:00000000:00000000:00000000:00000000 """

    usable_size = Size(
        data_key="usable_size",
    )
    r""" The usable_size field of the disk.

Example: 959934889984 """

    vendor = fields.Str(
        data_key="vendor",
    )
    r""" The vendor field of the disk.

Example: NETAPP """

    @property
    def resource(self):
        return Disk

    gettable_fields = [
        "aggregates.links",
        "aggregates.name",
        "aggregates.uuid",
        "bay",
        "bytes_per_sector",
        "class_",
        "container_type",
        "dr_node.name",
        "dr_node.uuid",
        "drawer",
        "effective_type",
        "error",
        "fips_certified",
        "firmware_version",
        "home_node.links",
        "home_node.name",
        "home_node.uuid",
        "key_id",
        "local",
        "model",
        "name",
        "node.links",
        "node.name",
        "node.uuid",
        "outage",
        "paths",
        "pool",
        "protection_mode",
        "rated_life_used_percent",
        "rpm",
        "sector_count",
        "self_encrypting",
        "serial_number",
        "shelf.links",
        "shelf.uid",
        "state",
        "stats",
        "type",
        "uid",
        "usable_size",
        "vendor",
    ]
    """aggregates.links,aggregates.name,aggregates.uuid,bay,bytes_per_sector,class_,container_type,dr_node.name,dr_node.uuid,drawer,effective_type,error,fips_certified,firmware_version,home_node.links,home_node.name,home_node.uuid,key_id,local,model,name,node.links,node.name,node.uuid,outage,paths,pool,protection_mode,rated_life_used_percent,rpm,sector_count,self_encrypting,serial_number,shelf.links,shelf.uid,state,stats,type,uid,usable_size,vendor,"""

    patchable_fields = [
        "drawer",
        "encryption_operation",
        "key_id",
        "node.name",
        "node.uuid",
        "outage",
        "stats",
    ]
    """drawer,encryption_operation,key_id,node.name,node.uuid,outage,stats,"""

    postable_fields = [
        "drawer",
        "key_id",
        "outage",
        "stats",
    ]
    """drawer,key_id,outage,stats,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Disk.get_collection(fields=field)]
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
            raise NetAppRestError("Disk modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Disk(Resource):
    """Allows interaction with Disk objects on the host"""

    _schema = DiskSchema
    _path = "/api/storage/disks"
    _keys = ["name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of disks.
### Related ONTAP commands
* `storage disk show`
### Learn more
* [`DOC /storage/disks`](#docs-storage-storage_disks)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="disk show")
        def disk_show(
            fields: List[Choices.define(["bay", "bytes_per_sector", "class_", "container_type", "effective_type", "encryption_operation", "fips_certified", "firmware_version", "local", "model", "name", "pool", "protection_mode", "rated_life_used_percent", "rpm", "sector_count", "self_encrypting", "serial_number", "state", "type", "uid", "usable_size", "vendor", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of Disk resources

            Args:
                bay: Disk shelf bay
                bytes_per_sector: Bytes per sector.
                class_: Disk class
                container_type: Type of overlying disk container
                effective_type: Effective Disk type
                encryption_operation: This field should only be set as a query parameter in a PATCH operation. It is input only and won't be returned by a subsequent GET. 
                fips_certified: 
                firmware_version: 
                local: Indicates if a disk is locally attached versus being remotely attached. A locally attached disk resides in the same proximity as the host cluster versus been attached to the remote cluster. 
                model: 
                name: Cluster-wide disk name
                pool: Pool to which disk is assigned
                protection_mode: Mode of drive data protection and FIPS compliance. Possible values are: - _open_ - Data is unprotected - _data_ - Data protection only, without FIPS compliance - _part_ - Data is unprotected; other FIPS compliance settings present - _full_ - Full data and FIPS compliance protection - _miss_ - Protection mode information is not available 
                rated_life_used_percent: Percentage of rated life used
                rpm: Revolutions per minute
                sector_count: Number of sectors on the disk.
                self_encrypting: 
                serial_number: 
                state: State
                type: Disk interface type
                uid: The unique identifier for a disk
                usable_size: 
                vendor: 
            """

            kwargs = {}
            if bay is not None:
                kwargs["bay"] = bay
            if bytes_per_sector is not None:
                kwargs["bytes_per_sector"] = bytes_per_sector
            if class_ is not None:
                kwargs["class_"] = class_
            if container_type is not None:
                kwargs["container_type"] = container_type
            if effective_type is not None:
                kwargs["effective_type"] = effective_type
            if encryption_operation is not None:
                kwargs["encryption_operation"] = encryption_operation
            if fips_certified is not None:
                kwargs["fips_certified"] = fips_certified
            if firmware_version is not None:
                kwargs["firmware_version"] = firmware_version
            if local is not None:
                kwargs["local"] = local
            if model is not None:
                kwargs["model"] = model
            if name is not None:
                kwargs["name"] = name
            if pool is not None:
                kwargs["pool"] = pool
            if protection_mode is not None:
                kwargs["protection_mode"] = protection_mode
            if rated_life_used_percent is not None:
                kwargs["rated_life_used_percent"] = rated_life_used_percent
            if rpm is not None:
                kwargs["rpm"] = rpm
            if sector_count is not None:
                kwargs["sector_count"] = sector_count
            if self_encrypting is not None:
                kwargs["self_encrypting"] = self_encrypting
            if serial_number is not None:
                kwargs["serial_number"] = serial_number
            if state is not None:
                kwargs["state"] = state
            if type is not None:
                kwargs["type"] = type
            if uid is not None:
                kwargs["uid"] = uid
            if usable_size is not None:
                kwargs["usable_size"] = usable_size
            if vendor is not None:
                kwargs["vendor"] = vendor
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return Disk.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Disk resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["Disk"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates disk ownership, changes authentication keys, or sanitizes disks.
### Related ONTAP commands
* `storage disk assign`
* `storage encryption disk modify -data-key-id`
* `storage encryption disk sanitize`
* `security key-manager key query -key-type NSE-AK`
### Learn more
* [`DOC /storage/disks`](#docs-storage-storage_disks)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)



    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of disks.
### Related ONTAP commands
* `storage disk show`
### Learn more
* [`DOC /storage/disks`](#docs-storage-storage_disks)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific disk.
### Related ONTAP commands
* `storage disk show`
### Learn more
* [`DOC /storage/disks`](#docs-storage-storage_disks)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)





