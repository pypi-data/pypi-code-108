r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Fibre Channel (FC) ports are the physical ports of FC adapters on ONTAP cluster nodes that can be connected to FC networks to provide FC network connectivity. An FC port defines the location of an FC interface within the ONTAP cluster.<br/>
The Fibre Channel port REST API allows you to discover FC ports, obtain status information for FC ports, and configure FC port properties. POST and DELETE requests are not supported. You must physically add and remove FC adapters to ONTAP nodes to create and remove ports from the ONTAP cluster.
## Performance monitoring
Performance of an FC port can be monitored by observing the `metric.*` and `statistics.*` properties. These properties show the performance of an FC port in terms of IOPS, latency, and throughput. The `metric.*` properties denote an average, whereas `statistics.*` properties denote a real-time monotonically increasing value aggregated across all nodes.
## Examples
### Retrieving all FC ports
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcPort

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(FcPort.get_collection()))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    FcPort(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/3c768e01-1abc-4b3b-b7c0-629ceb62a497"
                    }
                },
                "uuid": "3c768e01-1abc-4b3b-b7c0-629ceb62a497",
                "name": "node1",
            },
            "uuid": "931b20f8-b047-11e8-9af3-005056bb838e",
            "name": "0a",
            "_links": {
                "self": {
                    "href": "/api/network/fc/ports/931b20f8-b047-11e8-9af3-005056bb838e"
                }
            },
        }
    ),
    FcPort(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/3c768e01-1abc-4b3b-b7c0-629ceb62a497"
                    }
                },
                "uuid": "3c768e01-1abc-4b3b-b7c0-629ceb62a497",
                "name": "node1",
            },
            "uuid": "931b23f7-b047-11e8-9af3-005056bb838e",
            "name": "0b",
            "_links": {
                "self": {
                    "href": "/api/network/fc/ports/931b23f7-b047-11e8-9af3-005056bb838e"
                }
            },
        }
    ),
    FcPort(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/3c768e01-1abc-4b3b-b7c0-629ceb62a497"
                    }
                },
                "uuid": "3c768e01-1abc-4b3b-b7c0-629ceb62a497",
                "name": "node1",
            },
            "uuid": "931b25ba-b047-11e8-9af3-005056bb838e",
            "name": "0c",
            "_links": {
                "self": {
                    "href": "/api/network/fc/ports/931b25ba-b047-11e8-9af3-005056bb838e"
                }
            },
        }
    ),
    FcPort(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/3c768e01-1abc-4b3b-b7c0-629ceb62a497"
                    }
                },
                "uuid": "3c768e01-1abc-4b3b-b7c0-629ceb62a497",
                "name": "node1",
            },
            "uuid": "931b2748-b047-11e8-9af3-005056bb838e",
            "name": "0d",
            "_links": {
                "self": {
                    "href": "/api/network/fc/ports/931b2748-b047-11e8-9af3-005056bb838e"
                }
            },
        }
    ),
    FcPort(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/3c768e01-1abc-4b3b-b7c0-629ceb62a497"
                    }
                },
                "uuid": "3c768e01-1abc-4b3b-b7c0-629ceb62a497",
                "name": "node1",
            },
            "uuid": "931b28c2-b047-11e8-9af3-005056bb838e",
            "name": "0e",
            "_links": {
                "self": {
                    "href": "/api/network/fc/ports/931b28c2-b047-11e8-9af3-005056bb838e"
                }
            },
        }
    ),
    FcPort(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/3c768e01-1abc-4b3b-b7c0-629ceb62a497"
                    }
                },
                "uuid": "3c768e01-1abc-4b3b-b7c0-629ceb62a497",
                "name": "node1",
            },
            "uuid": "931b2a7b-b047-11e8-9af3-005056bb838e",
            "name": "0f",
            "_links": {
                "self": {
                    "href": "/api/network/fc/ports/931b2a7b-b047-11e8-9af3-005056bb838e"
                }
            },
        }
    ),
    FcPort(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/3c768e01-1abc-4b3b-b7c0-629ceb62a497"
                    }
                },
                "uuid": "3c768e01-1abc-4b3b-b7c0-629ceb62a497",
                "name": "node1",
            },
            "uuid": "931b2e2b-b047-11e8-9af3-005056bb838e",
            "name": "1b",
            "_links": {
                "self": {
                    "href": "/api/network/fc/ports/931b2e2b-b047-11e8-9af3-005056bb838e"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving all FC ports with state _online_
The `state` query parameter is used to perform the query.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcPort

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(FcPort.get_collection(state="online")))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    FcPort(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/3c768e01-1abc-4b3b-b7c0-629ceb62a497"
                    }
                },
                "uuid": "3c768e01-1abc-4b3b-b7c0-629ceb62a497",
                "name": "node1",
            },
            "uuid": "931b20f8-b047-11e8-9af3-005056bb838e",
            "state": "online",
            "name": "0a",
            "_links": {
                "self": {
                    "href": "/api/network/fc/ports/931b20f8-b047-11e8-9af3-005056bb838e"
                }
            },
        }
    ),
    FcPort(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/3c768e01-1abc-4b3b-b7c0-629ceb62a497"
                    }
                },
                "uuid": "3c768e01-1abc-4b3b-b7c0-629ceb62a497",
                "name": "node1",
            },
            "uuid": "931b23f7-b047-11e8-9af3-005056bb838e",
            "state": "online",
            "name": "0b",
            "_links": {
                "self": {
                    "href": "/api/network/fc/ports/931b23f7-b047-11e8-9af3-005056bb838e"
                }
            },
        }
    ),
    FcPort(
        {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/3c768e01-1abc-4b3b-b7c0-629ceb62a497"
                    }
                },
                "uuid": "3c768e01-1abc-4b3b-b7c0-629ceb62a497",
                "name": "node1",
            },
            "uuid": "931b25ba-b047-11e8-9af3-005056bb838e",
            "state": "online",
            "name": "0c",
            "_links": {
                "self": {
                    "href": "/api/network/fc/ports/931b25ba-b047-11e8-9af3-005056bb838e"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving an FC port
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcPort

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FcPort(uuid="931b20f8-b047-11e8-9af3-005056bb838e")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
FcPort(
    {
        "wwnn": "50:0a:09:80:bb:83:8e:00",
        "node": {
            "_links": {
                "self": {
                    "href": "/api/cluster/nodes/5a534a72-b047-11e8-9af3-005056bb838e"
                }
            },
            "uuid": "5a534a72-b047-11e8-9af3-005056bb838e",
            "name": "node1",
        },
        "enabled": True,
        "fabric": {
            "connected_speed": 8,
            "port_address": "52100",
            "connected": True,
            "name": "55:0e:b1:a0:20:40:80:00",
            "switch_port": "ssan-g620-03:1",
        },
        "physical_protocol": "fibre_channel",
        "statistics": {
            "iops_raw": {"total": 3, "write": 0, "read": 0, "other": 3},
            "status": "ok",
            "timestamp": "2019-04-09T05:50:42+00:00",
            "latency_raw": {"total": 38298, "write": 0, "read": 0, "other": 38298},
            "throughput_raw": {"total": 0, "write": 0, "read": 0},
        },
        "supported_protocols": ["fcp"],
        "uuid": "931b20f8-b047-11e8-9af3-005056bb838e",
        "wwpn": "50:0a:09:82:bb:83:8e:00",
        "state": "online",
        "transceiver": {
            "manufacturer": "ACME",
            "form_factor": "SFP",
            "part_number": "1000",
            "capabilities": [4, 8],
        },
        "speed": {"maximum": "8", "configured": "auto"},
        "metric": {
            "status": "ok",
            "timestamp": "2019-04-09T05:50:15+00:00",
            "latency": {"total": 0, "write": 0, "read": 0, "other": 0},
            "throughput": {"total": 0, "write": 0, "read": 0},
            "duration": "PT15S",
            "iops": {"total": 0, "write": 0, "read": 0, "other": 0},
        },
        "description": "Fibre Channel Target Adapter 0a (ACME Fibre Channel Adapter, rev. 1.0.0, 8G)",
        "name": "0a",
        "_links": {
            "self": {
                "href": "/api/network/fc/ports/931b20f8-b047-11e8-9af3-005056bb838e"
            }
        },
    }
)

```
</div>
</div>

---
### Disabling an FC port
If an active FC interface exists on an FC port, the port cannot be disabled.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcPort

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FcPort(uuid="931b20f8-b047-11e8-9af3-005056bb838e")
    resource.enabled = False
    resource.patch()

```

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


__all__ = ["FcPort", "FcPortSchema"]
__pdoc__ = {
    "FcPortSchema.resource": False,
    "FcPort.fc_port_show": False,
    "FcPort.fc_port_create": False,
    "FcPort.fc_port_modify": False,
    "FcPort.fc_port_delete": False,
}


class FcPortSchema(ResourceSchema):
    """The fields of the FcPort object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the fc_port. """

    description = fields.Str(
        data_key="description",
    )
    r""" A description of the FC port.


Example: Fibre Channel Target Adapter 0a (ACME Fibre Channel Adapter, rev. 1.0.0, 8G) """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" The administrative state of the FC port. If this property is set to _false_, all FC connectivity to FC interfaces are blocked. Optional in PATCH. """

    fabric = fields.Nested("netapp_ontap.models.fc_port_fabric.FcPortFabricSchema", data_key="fabric", unknown=EXCLUDE)
    r""" The fabric field of the fc_port. """

    interface_count = Size(
        data_key="interface_count",
    )
    r""" The number of FC interfaces currently provisioned on this port. This property is not supported in an SVM context. """

    metric = fields.Nested("netapp_ontap.models.performance_metric_reduced_throughput.PerformanceMetricReducedThroughputSchema", data_key="metric", unknown=EXCLUDE)
    r""" The metric field of the fc_port. """

    name = fields.Str(
        data_key="name",
    )
    r""" The FC port name.


Example: 0a """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the fc_port. """

    physical_protocol = fields.Str(
        data_key="physical_protocol",
        validate=enum_validation(['fibre_channel', 'ethernet']),
    )
    r""" The physical network protocol of the FC port.


Valid choices:

* fibre_channel
* ethernet """

    speed = fields.Nested("netapp_ontap.models.fc_port_speed.FcPortSpeedSchema", data_key="speed", unknown=EXCLUDE)
    r""" The speed field of the fc_port. """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['startup', 'link_not_connected', 'online', 'link_disconnected', 'offlined_by_user', 'offlined_by_system', 'node_offline', 'unknown']),
    )
    r""" The operational state of the FC port.
- startup - The port is booting up.
- link_not_connected - The port has finished initialization, but a link with the fabric is not established.
- online - The port is initialized and a link with the fabric has been established.
- link_disconnected - The link was present at one point on this port but is currently not established.
- offlined_by_user - The port is administratively disabled.
- offlined_by_system - The port is set to offline by the system. This happens when the port encounters too many errors.
- node_offline - The state information for the port cannot be retrieved. The node is offline or inaccessible.


Valid choices:

* startup
* link_not_connected
* online
* link_disconnected
* offlined_by_user
* offlined_by_system
* node_offline
* unknown """

    statistics = fields.Nested("netapp_ontap.models.performance_metric_raw_reduced_throughput.PerformanceMetricRawReducedThroughputSchema", data_key="statistics", unknown=EXCLUDE)
    r""" The statistics field of the fc_port. """

    supported_protocols = fields.List(fields.Str, data_key="supported_protocols")
    r""" The network protocols supported by the FC port. """

    transceiver = fields.Nested("netapp_ontap.models.fc_port_transceiver.FcPortTransceiverSchema", data_key="transceiver", unknown=EXCLUDE)
    r""" The transceiver field of the fc_port. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The unique identifier of the FC port.


Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    wwnn = fields.Str(
        data_key="wwnn",
    )
    r""" The base world wide node name (WWNN) for the FC port.


Example: 20:00:00:50:56:b4:13:a8 """

    wwpn = fields.Str(
        data_key="wwpn",
    )
    r""" The base world wide port name (WWPN) for the FC port.


Example: 20:00:00:50:56:b4:13:a8 """

    @property
    def resource(self):
        return FcPort

    gettable_fields = [
        "links",
        "description",
        "enabled",
        "fabric",
        "interface_count",
        "metric",
        "name",
        "node.links",
        "node.name",
        "node.uuid",
        "physical_protocol",
        "speed",
        "state",
        "statistics",
        "supported_protocols",
        "transceiver",
        "uuid",
        "wwnn",
        "wwpn",
    ]
    """links,description,enabled,fabric,interface_count,metric,name,node.links,node.name,node.uuid,physical_protocol,speed,state,statistics,supported_protocols,transceiver,uuid,wwnn,wwpn,"""

    patchable_fields = [
        "enabled",
        "fabric",
        "node.name",
        "node.uuid",
        "speed",
        "transceiver",
    ]
    """enabled,fabric,node.name,node.uuid,speed,transceiver,"""

    postable_fields = [
        "enabled",
        "fabric",
        "node.name",
        "node.uuid",
        "speed",
        "transceiver",
    ]
    """enabled,fabric,node.name,node.uuid,speed,transceiver,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FcPort.get_collection(fields=field)]
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
            raise NetAppRestError("FcPort modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FcPort(Resource):
    r""" A Fibre Channel (FC) port is the physical port of an FC adapter on an ONTAP cluster node that can be connected to an FC network to provide FC network connectivity. An FC port defines the location of an FC interface within the ONTAP cluster. """

    _schema = FcPortSchema
    _path = "/api/network/fc/ports"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves FC ports.<br/>
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `fabric.name`
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `network fcp adapter show`
### Learn more
* [`DOC /network/fc/ports`](#docs-networking-network_fc_ports)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fc port show")
        def fc_port_show(
            fields: List[Choices.define(["description", "enabled", "interface_count", "name", "physical_protocol", "state", "supported_protocols", "uuid", "wwnn", "wwpn", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of FcPort resources

            Args:
                description: A description of the FC port. 
                enabled: The administrative state of the FC port. If this property is set to _false_, all FC connectivity to FC interfaces are blocked. Optional in PATCH. 
                interface_count: The number of FC interfaces currently provisioned on this port. This property is not supported in an SVM context. 
                name: The FC port name. 
                physical_protocol: The physical network protocol of the FC port. 
                state: The operational state of the FC port. - startup - The port is booting up. - link_not_connected - The port has finished initialization, but a link with the fabric is not established. - online - The port is initialized and a link with the fabric has been established. - link_disconnected - The link was present at one point on this port but is currently not established. - offlined_by_user - The port is administratively disabled. - offlined_by_system - The port is set to offline by the system. This happens when the port encounters too many errors. - node_offline - The state information for the port cannot be retrieved. The node is offline or inaccessible. 
                supported_protocols: The network protocols supported by the FC port. 
                uuid: The unique identifier of the FC port. 
                wwnn: The base world wide node name (WWNN) for the FC port. 
                wwpn: The base world wide port name (WWPN) for the FC port. 
            """

            kwargs = {}
            if description is not None:
                kwargs["description"] = description
            if enabled is not None:
                kwargs["enabled"] = enabled
            if interface_count is not None:
                kwargs["interface_count"] = interface_count
            if name is not None:
                kwargs["name"] = name
            if physical_protocol is not None:
                kwargs["physical_protocol"] = physical_protocol
            if state is not None:
                kwargs["state"] = state
            if supported_protocols is not None:
                kwargs["supported_protocols"] = supported_protocols
            if uuid is not None:
                kwargs["uuid"] = uuid
            if wwnn is not None:
                kwargs["wwnn"] = wwnn
            if wwpn is not None:
                kwargs["wwpn"] = wwpn
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return FcPort.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all FcPort resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["FcPort"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an FC port.
### Related ONTAP commands
* `network fcp adapter modify`
### Learn more
* [`DOC /network/fc/ports`](#docs-networking-network_fc_ports)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)



    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves FC ports.<br/>
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `fabric.name`
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `network fcp adapter show`
### Learn more
* [`DOC /network/fc/ports`](#docs-networking-network_fc_ports)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an FC port.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `fabric.name`
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `network fcp adapter show`
### Learn more
* [`DOC /network/fc/ports`](#docs-networking-network_fc_ports)
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
        r"""Updates an FC port.
### Related ONTAP commands
* `network fcp adapter modify`
### Learn more
* [`DOC /network/fc/ports`](#docs-networking-network_fc_ports)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fc port modify")
        async def fc_port_modify(
        ) -> ResourceTable:
            """Modify an instance of a FcPort resource

            Args:
                description: A description of the FC port. 
                query_description: A description of the FC port. 
                enabled: The administrative state of the FC port. If this property is set to _false_, all FC connectivity to FC interfaces are blocked. Optional in PATCH. 
                query_enabled: The administrative state of the FC port. If this property is set to _false_, all FC connectivity to FC interfaces are blocked. Optional in PATCH. 
                interface_count: The number of FC interfaces currently provisioned on this port. This property is not supported in an SVM context. 
                query_interface_count: The number of FC interfaces currently provisioned on this port. This property is not supported in an SVM context. 
                name: The FC port name. 
                query_name: The FC port name. 
                physical_protocol: The physical network protocol of the FC port. 
                query_physical_protocol: The physical network protocol of the FC port. 
                state: The operational state of the FC port. - startup - The port is booting up. - link_not_connected - The port has finished initialization, but a link with the fabric is not established. - online - The port is initialized and a link with the fabric has been established. - link_disconnected - The link was present at one point on this port but is currently not established. - offlined_by_user - The port is administratively disabled. - offlined_by_system - The port is set to offline by the system. This happens when the port encounters too many errors. - node_offline - The state information for the port cannot be retrieved. The node is offline or inaccessible. 
                query_state: The operational state of the FC port. - startup - The port is booting up. - link_not_connected - The port has finished initialization, but a link with the fabric is not established. - online - The port is initialized and a link with the fabric has been established. - link_disconnected - The link was present at one point on this port but is currently not established. - offlined_by_user - The port is administratively disabled. - offlined_by_system - The port is set to offline by the system. This happens when the port encounters too many errors. - node_offline - The state information for the port cannot be retrieved. The node is offline or inaccessible. 
                supported_protocols: The network protocols supported by the FC port. 
                query_supported_protocols: The network protocols supported by the FC port. 
                uuid: The unique identifier of the FC port. 
                query_uuid: The unique identifier of the FC port. 
                wwnn: The base world wide node name (WWNN) for the FC port. 
                query_wwnn: The base world wide node name (WWNN) for the FC port. 
                wwpn: The base world wide port name (WWPN) for the FC port. 
                query_wwpn: The base world wide port name (WWPN) for the FC port. 
            """

            kwargs = {}
            changes = {}
            if query_description is not None:
                kwargs["description"] = query_description
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_interface_count is not None:
                kwargs["interface_count"] = query_interface_count
            if query_name is not None:
                kwargs["name"] = query_name
            if query_physical_protocol is not None:
                kwargs["physical_protocol"] = query_physical_protocol
            if query_state is not None:
                kwargs["state"] = query_state
            if query_supported_protocols is not None:
                kwargs["supported_protocols"] = query_supported_protocols
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid
            if query_wwnn is not None:
                kwargs["wwnn"] = query_wwnn
            if query_wwpn is not None:
                kwargs["wwpn"] = query_wwpn

            if description is not None:
                changes["description"] = description
            if enabled is not None:
                changes["enabled"] = enabled
            if interface_count is not None:
                changes["interface_count"] = interface_count
            if name is not None:
                changes["name"] = name
            if physical_protocol is not None:
                changes["physical_protocol"] = physical_protocol
            if state is not None:
                changes["state"] = state
            if supported_protocols is not None:
                changes["supported_protocols"] = supported_protocols
            if uuid is not None:
                changes["uuid"] = uuid
            if wwnn is not None:
                changes["wwnn"] = wwnn
            if wwpn is not None:
                changes["wwpn"] = wwpn

            if hasattr(FcPort, "find"):
                resource = FcPort.find(
                    **kwargs
                )
            else:
                resource = FcPort()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify FcPort: %s" % err)



