r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Retrieving storage bridge information
The storage bridge GET API retrieves all of the bridges in the cluster.
<br/>
---
## Examples
### 1) Retrieves a list of bridges from the cluster
#### The following example shows the response with a list of bridges from the cluster:
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import StorageBridge

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(StorageBridge.get_collection()))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    StorageBridge({"wwn": "2000001086a18100", "name": "ATTO_2000001086a18100"}),
    StorageBridge({"wwn": "2000001086a18380", "name": "ATTO_2000001086a18380"}),
]

```
</div>
</div>

---
### 2) Retrieves a specific bridge from the cluster
#### The following example shows the response of the requested bridge. If there is no bridge with the requested wwn, an error is returned.
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import StorageBridge

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = StorageBridge(wwn="2000001086a18100")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
StorageBridge(
    {
        "sas_ports": [
            {
                "data_rate_capability": 12.0,
                "enabled": True,
                "phy_3": {"state": "online"},
                "wwn": "5001086000a18100",
                "id": 1,
                "phy_4": {"state": "online"},
                "state": "online",
                "negotiated_data_rate": 6.0,
                "phy_1": {"state": "online"},
                "cable": {
                    "vendor": "Molex Inc.",
                    "part_number": "112-00431",
                    "serial_number": "618130935",
                    "technology": "Passive Copper 5m ID:00",
                },
                "phy_2": {"state": "online"},
            },
            {
                "data_rate_capability": 12.0,
                "enabled": False,
                "phy_3": {"state": "offline"},
                "wwn": "5001086000a18104",
                "phy_4": {"state": "offline"},
                "state": "offline",
                "negotiated_data_rate": 0.0,
                "phy_1": {"state": "offline"},
                "phy_2": {"state": "offline"},
            },
            {
                "data_rate_capability": 12.0,
                "enabled": False,
                "phy_3": {"state": "offline"},
                "wwn": "5001086000a18108",
                "phy_4": {"state": "offline"},
                "state": "offline",
                "negotiated_data_rate": 0.0,
                "phy_1": {"state": "offline"},
                "phy_2": {"state": "offline"},
            },
            {
                "data_rate_capability": 12.0,
                "enabled": False,
                "phy_3": {"state": "offline"},
                "wwn": "5001086000a1810c",
                "phy_4": {"state": "offline"},
                "state": "offline",
                "negotiated_data_rate": 0.0,
                "phy_1": {"state": "offline"},
                "phy_2": {"state": "offline"},
            },
        ],
        "temperature_sensor": {
            "minimum": 0,
            "maximum": 90,
            "reading": 54,
            "state": "ok",
            "name": "Chassis Temperature Sensor",
        },
        "last_reboot": {
            "time": "2020-12-09T00:47:58-05:00",
            "reason": {
                "code": "39321683",
                "message": 'Reason: "FirmwareRestart Command".',
            },
        },
        "dram_single_bit_error_count": 0,
        "serial_number": "FB7500N102450",
        "symbolic_name": "RTP-FCSAS02-41KK10",
        "managed_by": "in_band",
        "monitoring_enabled": True,
        "wwn": "2000001086a18100",
        "ip_address": "10.226.57.178",
        "vendor": "atto",
        "state": "ok",
        "chassis_throughput_state": "ok",
        "firmware_version": "3.10 007A",
        "fc_ports": [
            {
                "data_rate_capability": 16.0,
                "enabled": True,
                "wwn": "2100001086a18100",
                "id": 1,
                "configured_data_rate": 8.0,
                "state": "online",
                "negotiated_data_rate": 8.0,
                "sfp": {
                    "vendor": "FINISAR CORP.",
                    "data_rate_capability": 16.0,
                    "part_number": "FTLF8529P3BCV",
                    "serial_number": "UW106SA",
                },
                "peer_wwn": "0000000000000000",
            },
            {
                "data_rate_capability": 16.0,
                "enabled": True,
                "wwn": "2200001086a18100",
                "id": 2,
                "configured_data_rate": 16.0,
                "state": "online",
                "negotiated_data_rate": 16.0,
                "sfp": {
                    "vendor": "FINISAR CORP.",
                    "data_rate_capability": 16.0,
                    "part_number": "FTLF8529P3BCV",
                    "serial_number": "UW1072B",
                },
                "peer_wwn": "0000000000000000",
            },
        ],
        "model": "FibreBridge 7500N",
        "security_enabled": False,
        "power_supply_units": [
            {"state": "ok", "name": "A"},
            {"state": "ok", "name": "B"},
        ],
        "paths": [
            {
                "target_port": {"wwn": "2100001086a18380"},
                "node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/ecc3d992-3a86-11eb-9fab-00a0985a6024"
                        }
                    },
                    "uuid": "ecc3d992-3a86-11eb-9fab-00a0985a6024",
                    "name": "sti8080mcc-htp-005",
                },
                "name": "0e",
            }
        ],
        "name": "ATTO_2000001086a18100",
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


__all__ = ["StorageBridge", "StorageBridgeSchema"]
__pdoc__ = {
    "StorageBridgeSchema.resource": False,
    "StorageBridge.storage_bridge_show": False,
    "StorageBridge.storage_bridge_create": False,
    "StorageBridge.storage_bridge_modify": False,
    "StorageBridge.storage_bridge_delete": False,
}


class StorageBridgeSchema(ResourceSchema):
    """The fields of the StorageBridge object"""

    chassis_throughput_state = fields.Str(
        data_key="chassis_throughput_state",
        validate=enum_validation(['ok', 'warning']),
    )
    r""" Chassis throughput status

Valid choices:

* ok
* warning """

    dram_single_bit_error_count = Size(
        data_key="dram_single_bit_error_count",
    )
    r""" The dram_single_bit_error_count field of the storage_bridge. """

    errors = fields.List(fields.Nested("netapp_ontap.models.storage_bridge_errors.StorageBridgeErrorsSchema", unknown=EXCLUDE), data_key="errors")
    r""" The errors field of the storage_bridge. """

    fc_ports = fields.List(fields.Nested("netapp_ontap.models.storage_bridge_fc_ports.StorageBridgeFcPortsSchema", unknown=EXCLUDE), data_key="fc_ports")
    r""" The fc_ports field of the storage_bridge. """

    firmware_version = fields.Str(
        data_key="firmware_version",
    )
    r""" Bridge firmware version

Example: 4.10 007A """

    ip_address = fields.Str(
        data_key="ip_address",
    )
    r""" IP Address """

    last_reboot = fields.Nested("netapp_ontap.models.storage_bridge_last_reboot.StorageBridgeLastRebootSchema", data_key="last_reboot", unknown=EXCLUDE)
    r""" The last_reboot field of the storage_bridge. """

    managed_by = fields.Str(
        data_key="managed_by",
        validate=enum_validation(['snmp', 'in_band']),
    )
    r""" The managed_by field of the storage_bridge.

Valid choices:

* snmp
* in_band """

    model = fields.Str(
        data_key="model",
    )
    r""" Bridge model

Example: FibreBridge6500N """

    monitoring_enabled = fields.Boolean(
        data_key="monitoring_enabled",
    )
    r""" Indicates whether monitoring is enabled for the bridge. """

    name = fields.Str(
        data_key="name",
    )
    r""" Bridge name

Example: ATTO_FibreBridge6500N_1 """

    paths = fields.List(fields.Nested("netapp_ontap.models.storage_bridge_paths.StorageBridgePathsSchema", unknown=EXCLUDE), data_key="paths")
    r""" The paths field of the storage_bridge. """

    power_supply_units = fields.List(fields.Nested("netapp_ontap.models.storage_bridge_power_supply_units.StorageBridgePowerSupplyUnitsSchema", unknown=EXCLUDE), data_key="power_supply_units")
    r""" The power_supply_units field of the storage_bridge. """

    sas_ports = fields.List(fields.Nested("netapp_ontap.models.storage_bridge_sas_ports.StorageBridgeSasPortsSchema", unknown=EXCLUDE), data_key="sas_ports")
    r""" The sas_ports field of the storage_bridge. """

    security_enabled = fields.Boolean(
        data_key="security_enabled",
    )
    r""" Indicates whether security is enabled for the bridge. """

    serial_number = fields.Str(
        data_key="serial_number",
    )
    r""" Bridge serial number

Example: FB7600N100004 """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['unknown', 'ok', 'error']),
    )
    r""" Bridge state

Valid choices:

* unknown
* ok
* error """

    symbolic_name = fields.Str(
        data_key="symbolic_name",
    )
    r""" Bridge symbolic name

Example: rtp-fcsas03-41kk11 """

    temperature_sensor = fields.Nested("netapp_ontap.models.storage_bridge_temperature_sensor.StorageBridgeTemperatureSensorSchema", data_key="temperature_sensor", unknown=EXCLUDE)
    r""" The temperature_sensor field of the storage_bridge. """

    vendor = fields.Str(
        data_key="vendor",
        validate=enum_validation(['unknown', 'atto']),
    )
    r""" Bridge vendor

Valid choices:

* unknown
* atto """

    wwn = fields.Str(
        data_key="wwn",
    )
    r""" Bridge world wide name

Example: 2000001086600476 """

    @property
    def resource(self):
        return StorageBridge

    gettable_fields = [
        "chassis_throughput_state",
        "dram_single_bit_error_count",
        "errors",
        "fc_ports",
        "firmware_version",
        "ip_address",
        "last_reboot",
        "managed_by",
        "model",
        "monitoring_enabled",
        "name",
        "paths",
        "power_supply_units",
        "sas_ports",
        "security_enabled",
        "serial_number",
        "state",
        "symbolic_name",
        "temperature_sensor",
        "vendor",
        "wwn",
    ]
    """chassis_throughput_state,dram_single_bit_error_count,errors,fc_ports,firmware_version,ip_address,last_reboot,managed_by,model,monitoring_enabled,name,paths,power_supply_units,sas_ports,security_enabled,serial_number,state,symbolic_name,temperature_sensor,vendor,wwn,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in StorageBridge.get_collection(fields=field)]
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
            raise NetAppRestError("StorageBridge modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class StorageBridge(Resource):
    """Allows interaction with StorageBridge objects on the host"""

    _schema = StorageBridgeSchema
    _path = "/api/storage/bridges"
    _keys = ["wwn"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of bridges.
### Related ONTAP commands
* `storage bridge show`
### Learn more
* [`DOC /storage/bridges`](#docs-storage-storage_bridges)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="storage bridge show")
        def storage_bridge_show(
            fields: List[Choices.define(["chassis_throughput_state", "dram_single_bit_error_count", "firmware_version", "ip_address", "managed_by", "model", "monitoring_enabled", "name", "security_enabled", "serial_number", "state", "symbolic_name", "vendor", "wwn", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of StorageBridge resources

            Args:
                chassis_throughput_state: Chassis throughput status
                dram_single_bit_error_count: 
                firmware_version: Bridge firmware version
                ip_address: IP Address
                managed_by: 
                model: Bridge model
                monitoring_enabled: Indicates whether monitoring is enabled for the bridge.
                name: Bridge name
                security_enabled: Indicates whether security is enabled for the bridge.
                serial_number: Bridge serial number
                state: Bridge state
                symbolic_name: Bridge symbolic name
                vendor: Bridge vendor
                wwn: Bridge world wide name
            """

            kwargs = {}
            if chassis_throughput_state is not None:
                kwargs["chassis_throughput_state"] = chassis_throughput_state
            if dram_single_bit_error_count is not None:
                kwargs["dram_single_bit_error_count"] = dram_single_bit_error_count
            if firmware_version is not None:
                kwargs["firmware_version"] = firmware_version
            if ip_address is not None:
                kwargs["ip_address"] = ip_address
            if managed_by is not None:
                kwargs["managed_by"] = managed_by
            if model is not None:
                kwargs["model"] = model
            if monitoring_enabled is not None:
                kwargs["monitoring_enabled"] = monitoring_enabled
            if name is not None:
                kwargs["name"] = name
            if security_enabled is not None:
                kwargs["security_enabled"] = security_enabled
            if serial_number is not None:
                kwargs["serial_number"] = serial_number
            if state is not None:
                kwargs["state"] = state
            if symbolic_name is not None:
                kwargs["symbolic_name"] = symbolic_name
            if vendor is not None:
                kwargs["vendor"] = vendor
            if wwn is not None:
                kwargs["wwn"] = wwn
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return StorageBridge.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all StorageBridge resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of bridges.
### Related ONTAP commands
* `storage bridge show`
### Learn more
* [`DOC /storage/bridges`](#docs-storage-storage_bridges)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific bridge
### Related ONTAP commands
* `storage bridge show`
### Learn more
* [`DOC /storage/bridges`](#docs-storage-storage_bridges)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)





