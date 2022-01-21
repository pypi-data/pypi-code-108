r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Retrieving storage switch information
The storage switch GET API retrieves all of the switches in the cluster.
<br/>
---
## Examples
### 1) Retrieves a list of storage switches from the cluster
#### The following example shows the response with a list of storage switches in the cluster:
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import StorageSwitch

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(StorageSwitch.get_collection()))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    StorageSwitch({"name": "Brocade_10.226.57.206"}),
    StorageSwitch({"name": "Brocade_10.226.57.207"}),
    StorageSwitch({"name": "Brocade_10.226.57.208"}),
    StorageSwitch({"name": "Brocade_10.226.57.209"}),
]

```
</div>
</div>

---
### 2) Retrieves a specific storage switch from the cluster
#### The following example shows the response of the requested storage switch. If there is no storage switch with the requested name, an error is returned.
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import StorageSwitch

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = StorageSwitch(name="Brocade_10.226.57.206")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
StorageSwitch(
    {
        "local": False,
        "fans": [
            {"state": "ok", "name": "FAN #1", "speed": 7336},
            {"state": "ok", "name": "FAN #2", "speed": 7336},
        ],
        "role": "subordinate",
        "symbolic_name": "rtp-fc01-41kk11",
        "monitoring_enabled": True,
        "wwn": "100050eb1a1ef7d7",
        "temperature_sensors": [
            {"state": "ok", "name": "SLOT #0: TEMP #1", "reading": 52}
        ],
        "ip_address": "10.226.57.206",
        "vendor": "brocade",
        "state": "ok",
        "domain_id": 5,
        "connections": [
            {
                "source_port": {
                    "mode": "f_port",
                    "wwn": "200050eb1a236efd",
                    "name": "FC port 0/0",
                },
                "peer_port": {
                    "type": "fcvi_adapter",
                    "connection": "sti8020mcc-htp-006:fcvi_device_1",
                    "unique_id": "38993dc0-4ea1-11eb-9331-00a0985bd455",
                    "wwn": "2100000e1e30ac5f",
                },
            },
            {
                "source_port": {
                    "mode": "f_port",
                    "wwn": "200150eb1a236efd",
                    "name": "FC port 0/1",
                },
                "peer_port": {
                    "type": "fcp_adapter",
                    "connection": "sti8020mcc-htp-006:2b",
                    "unique_id": "38993dc0-4ea1-11eb-9331-00a0985bd455",
                    "wwn": "21000024ff72c0c9",
                },
            },
            {
                "source_port": {
                    "mode": "f_port",
                    "wwn": "200250eb1a236efd",
                    "name": "FC port 0/2",
                },
                "peer_port": {
                    "type": "fcp_adapter",
                    "connection": "sti8020mcc-htp-006:2d",
                    "unique_id": "38993dc0-4ea1-11eb-9331-00a0985bd455",
                    "wwn": "21000024ff72c0cb",
                },
            },
        ],
        "model": "Brocade6510",
        "ports": [
            {
                "mode": "f_port",
                "enabled": True,
                "wwn": "200050eb1a1ef7d7",
                "state": "online",
                "sfp": {
                    "type": "small_form_factor",
                    "transmitter_type": "short_wave_laser",
                    "serial_number": "HAA2140310058E5",
                },
                "name": "FC port 0/0",
                "speed": 16,
            },
            {
                "mode": "f_port",
                "enabled": True,
                "wwn": "200050eb1a1ef2d7",
                "state": "online",
                "sfp": {
                    "type": "small_form_factor",
                    "transmitter_type": "short_wave_laser",
                    "serial_number": "HAA2140310058E5",
                },
                "name": "FC port 0/1",
                "speed": 16,
            },
            {
                "mode": "f_port",
                "enabled": True,
                "wwn": "200050eb1a1ef7d0",
                "state": "online",
                "sfp": {
                    "type": "small_form_factor",
                    "transmitter_type": "short_wave_laser",
                    "serial_number": "HAA2140310058E5",
                },
                "name": "FC port 0/2",
                "speed": 16,
            },
            {
                "mode": "f_port",
                "enabled": True,
                "wwn": "200050eb1a1ef7d7",
                "state": "online",
                "sfp": {
                    "type": "small_form_factor",
                    "transmitter_type": "short_wave_laser",
                    "serial_number": "HAA2140310058E5",
                },
                "name": "FC port 0/3",
                "speed": 16,
            },
            {
                "mode": "f_port",
                "enabled": True,
                "wwn": "200050eb1a1ef2d7",
                "state": "online",
                "sfp": {
                    "type": "small_form_factor",
                    "transmitter_type": "short_wave_laser",
                    "serial_number": "HAA2140310058E5",
                },
                "name": "FC port 0/4",
                "speed": 16,
            },
            {
                "mode": "f_port",
                "enabled": True,
                "wwn": "200050eb1a1ef7d0",
                "state": "online",
                "sfp": {
                    "type": "small_form_factor",
                    "transmitter_type": "short_wave_laser",
                    "serial_number": "HAA2140310058E5",
                },
                "name": "FC port 0/5",
                "speed": 16,
            },
        ],
        "power_supply_units": [
            {"state": "ok", "name": "Power Supply #1"},
            {"state": "ok", "name": "Power Supply #2"},
        ],
        "paths": [
            {
                "port": {"name": "FC port 0/4", "speed": 8},
                "node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/382cb083-4416-11eb-ad1d-00a0985bd455"
                        }
                    },
                    "uuid": "382cb083-4416-11eb-ad1d-00a0985bd455",
                    "name": "sti8020mcc-htp-005",
                },
                "adapter": {
                    "type": "fcp_initiator",
                    "name": "2a",
                    "wwn": "21000024ff6c4bc0",
                },
            },
            {
                "port": {"name": "FC port 0/5", "speed": 8},
                "node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/382cb083-4416-11eb-ad1d-00a0985bd455"
                        }
                    },
                    "uuid": "382cb083-4416-11eb-ad1d-00a0985bd455",
                    "name": "sti8020mcc-htp-005",
                },
                "adapter": {
                    "type": "fcp_initiator",
                    "name": "2c",
                    "wwn": "21000024ff6c4bc2",
                },
            },
            {
                "port": {"name": "FC port 0/3", "speed": 16},
                "node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/382cb083-4416-11eb-ad1d-00a0985bd455"
                        }
                    },
                    "uuid": "382cb083-4416-11eb-ad1d-00a0985bd455",
                    "name": "sti8020mcc-htp-005",
                },
                "adapter": {
                    "type": "fc_vi",
                    "name": "fcvi_device_0",
                    "wwn": "2100000e1e09d5d2",
                },
            },
            {
                "port": {"name": "FC port 0/1", "speed": 8},
                "node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/364fbba8-4416-11eb-8e72-00a098431045"
                        }
                    },
                    "uuid": "364fbba8-4416-11eb-8e72-00a098431045",
                    "name": "sti8020mcc-htp-006",
                },
                "adapter": {
                    "type": "fcp_initiator",
                    "name": "2a",
                    "wwn": "21000024ff72c0c8",
                },
            },
            {
                "port": {"name": "FC port 0/2", "speed": 8},
                "node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/364fbba8-4416-11eb-8e72-00a098431045"
                        }
                    },
                    "uuid": "364fbba8-4416-11eb-8e72-00a098431045",
                    "name": "sti8020mcc-htp-006",
                },
                "adapter": {
                    "type": "fcp_initiator",
                    "name": "2c",
                    "wwn": "21000024ff72c0ca",
                },
            },
        ],
        "name": "Brocade_10.226.57.206",
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


__all__ = ["StorageSwitch", "StorageSwitchSchema"]
__pdoc__ = {
    "StorageSwitchSchema.resource": False,
    "StorageSwitch.storage_switch_show": False,
    "StorageSwitch.storage_switch_create": False,
    "StorageSwitch.storage_switch_modify": False,
    "StorageSwitch.storage_switch_delete": False,
}


class StorageSwitchSchema(ResourceSchema):
    """The fields of the StorageSwitch object"""

    connections = fields.List(fields.Nested("netapp_ontap.models.storage_switch_connections.StorageSwitchConnectionsSchema", unknown=EXCLUDE), data_key="connections")
    r""" The connections field of the storage_switch. """

    director_class = fields.Boolean(
        data_key="director_class",
    )
    r""" The director_class field of the storage_switch. """

    domain_id = Size(
        data_key="domain_id",
    )
    r""" Domain ID """

    errors = fields.List(fields.Nested("netapp_ontap.models.storage_switch_errors.StorageSwitchErrorsSchema", unknown=EXCLUDE), data_key="errors")
    r""" The errors field of the storage_switch. """

    fabric_name = fields.Str(
        data_key="fabric_name",
    )
    r""" Storage switch fabric name """

    fans = fields.List(fields.Nested("netapp_ontap.models.storage_switch_fans.StorageSwitchFansSchema", unknown=EXCLUDE), data_key="fans")
    r""" The fans field of the storage_switch. """

    firmware_version = fields.Str(
        data_key="firmware_version",
    )
    r""" Storage switch firmware version """

    ip_address = fields.Str(
        data_key="ip_address",
    )
    r""" IP Address """

    local = fields.Boolean(
        data_key="local",
    )
    r""" Indicates whether the storage switch is directly connected to the reporting cluster. """

    model = fields.Str(
        data_key="model",
    )
    r""" Storage switch model. """

    monitored_blades = fields.List(Size, data_key="monitored_blades")
    r""" Indicates the blades that are being monitored for a director-class switch. """

    monitoring_enabled = fields.Boolean(
        data_key="monitoring_enabled",
    )
    r""" Indicates whether monitoring is enabled for the storage switch. """

    name = fields.Str(
        data_key="name",
    )
    r""" Storage switch name """

    paths = fields.List(fields.Nested("netapp_ontap.models.storage_switch_paths.StorageSwitchPathsSchema", unknown=EXCLUDE), data_key="paths")
    r""" The paths field of the storage_switch. """

    ports = fields.List(fields.Nested("netapp_ontap.models.storage_switch_ports.StorageSwitchPortsSchema", unknown=EXCLUDE), data_key="ports")
    r""" The ports field of the storage_switch. """

    power_supply_units = fields.List(fields.Nested("netapp_ontap.models.storage_bridge_power_supply_units.StorageBridgePowerSupplyUnitsSchema", unknown=EXCLUDE), data_key="power_supply_units")
    r""" The power_supply_units field of the storage_switch. """

    role = fields.Str(
        data_key="role",
        validate=enum_validation(['unknown', 'primary', 'subordinate']),
    )
    r""" Storage switch role in fabric.

Valid choices:

* unknown
* primary
* subordinate """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['ok', 'error']),
    )
    r""" Storage switch state

Valid choices:

* ok
* error """

    symbolic_name = fields.Str(
        data_key="symbolic_name",
    )
    r""" Storage switch symbolic name """

    temperature_sensors = fields.List(fields.Nested("netapp_ontap.models.storage_switch_temperature_sensors.StorageSwitchTemperatureSensorsSchema", unknown=EXCLUDE), data_key="temperature_sensors")
    r""" The temperature_sensors field of the storage_switch. """

    vendor = fields.Str(
        data_key="vendor",
        validate=enum_validation(['unknown', 'brocade', 'cisco']),
    )
    r""" Storage switch vendor

Valid choices:

* unknown
* brocade
* cisco """

    vsans = fields.List(fields.Nested("netapp_ontap.models.storage_switch_vsans.StorageSwitchVsansSchema", unknown=EXCLUDE), data_key="vsans")
    r""" The vsans field of the storage_switch. """

    wwn = fields.Str(
        data_key="wwn",
    )
    r""" Storage switch world wide name """

    zones = fields.List(fields.Nested("netapp_ontap.models.storage_switch_zones.StorageSwitchZonesSchema", unknown=EXCLUDE), data_key="zones")
    r""" The zones field of the storage_switch. """

    @property
    def resource(self):
        return StorageSwitch

    gettable_fields = [
        "connections",
        "director_class",
        "domain_id",
        "errors",
        "fabric_name",
        "fans",
        "firmware_version",
        "ip_address",
        "local",
        "model",
        "monitored_blades",
        "monitoring_enabled",
        "name",
        "paths",
        "ports",
        "power_supply_units",
        "role",
        "state",
        "symbolic_name",
        "temperature_sensors",
        "vendor",
        "vsans",
        "wwn",
        "zones",
    ]
    """connections,director_class,domain_id,errors,fabric_name,fans,firmware_version,ip_address,local,model,monitored_blades,monitoring_enabled,name,paths,ports,power_supply_units,role,state,symbolic_name,temperature_sensors,vendor,vsans,wwn,zones,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in StorageSwitch.get_collection(fields=field)]
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
            raise NetAppRestError("StorageSwitch modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class StorageSwitch(Resource):
    r""" The Storage switch object describes the storage switch properties, features and cabling. """

    _schema = StorageSwitchSchema
    _path = "/api/storage/switches"
    _keys = ["name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of storage switches.
### Related ONTAP commands
* `storage switch show`
### Learn more
* [`DOC /storage/switches`](#docs-storage-storage_switches)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="storage switch show")
        def storage_switch_show(
            fields: List[Choices.define(["director_class", "domain_id", "fabric_name", "firmware_version", "ip_address", "local", "model", "monitored_blades", "monitoring_enabled", "name", "role", "state", "symbolic_name", "vendor", "wwn", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of StorageSwitch resources

            Args:
                director_class: 
                domain_id: Domain ID
                fabric_name: Storage switch fabric name
                firmware_version: Storage switch firmware version
                ip_address: IP Address
                local: Indicates whether the storage switch is directly connected to the reporting cluster.
                model: Storage switch model.
                monitored_blades: Indicates the blades that are being monitored for a director-class switch.
                monitoring_enabled: Indicates whether monitoring is enabled for the storage switch.
                name: Storage switch name
                role: Storage switch role in fabric.
                state: Storage switch state
                symbolic_name: Storage switch symbolic name
                vendor: Storage switch vendor
                wwn: Storage switch world wide name
            """

            kwargs = {}
            if director_class is not None:
                kwargs["director_class"] = director_class
            if domain_id is not None:
                kwargs["domain_id"] = domain_id
            if fabric_name is not None:
                kwargs["fabric_name"] = fabric_name
            if firmware_version is not None:
                kwargs["firmware_version"] = firmware_version
            if ip_address is not None:
                kwargs["ip_address"] = ip_address
            if local is not None:
                kwargs["local"] = local
            if model is not None:
                kwargs["model"] = model
            if monitored_blades is not None:
                kwargs["monitored_blades"] = monitored_blades
            if monitoring_enabled is not None:
                kwargs["monitoring_enabled"] = monitoring_enabled
            if name is not None:
                kwargs["name"] = name
            if role is not None:
                kwargs["role"] = role
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

            return StorageSwitch.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all StorageSwitch resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of storage switches.
### Related ONTAP commands
* `storage switch show`
### Learn more
* [`DOC /storage/switches`](#docs-storage-storage_switches)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific storage switch.
### Related ONTAP commands
* `storage switch show`
### Learn more
* [`DOC /storage/switches`](#docs-storage-storage_switches)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)





