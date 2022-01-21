r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Fibre Channel (FC) interfaces are the logical endpoints for FC network connections to an SVM. An FC interface provides FC access to storage within the interface SVM using either Fibre Channel Protocol or NVMe over FC (NVMe/FC).<br/>
The Fibre Channel interface REST API allows you to create, delete, update, and discover FC interfaces, and obtain status information for FC interfaces.<br/>
An FC interface is created on an FC port which is located on a cluster node. The FC port must be specified to identify the location of the interface for a POST or PATCH request that relocates an interface. You can identify the port by supplying either the node and port names or the port UUID.
## Performance monitoring
Performance of an FC interface can be monitored by observing the `metric.*` and `statistics.*` properties. These properties show the performance of an FC interface in terms of IOPS, latency, and throughput. The `metric.*` properties denote an average, whereas `statistics.*` properties denote a real-time monotonically increasing value aggregated across all nodes.
## Examples
### Creating an FC interface using the port node and name to identify the location
This example uses the `return_records` query parameter to retrieve the newly created FC interface in the POST response.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FcInterface()
    resource.svm = {"name": "svm1"}
    resource.name = "lif1"
    resource.location = {"home_port": {"name": "0a", "home_node": {"name": "node1"}}}
    resource.data_protocol = "fcp"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
FcInterface(
    {
        "enabled": True,
        "port_address": "9da2cb1",
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/cf300f5c-db83-11e8-bd46-005056bba0e0"}
            },
            "uuid": "cf300f5c-db83-11e8-bd46-005056bba0e0",
            "name": "svm1",
        },
        "data_protocol": "fcp",
        "uuid": "f6045b92-dec7-11e8-a733-005056bba0e0",
        "wwpn": "20:04:00:50:56:bb:a0:e0",
        "state": "down",
        "location": {
            "home_node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/bafe9b9f-db81-11e8-bd46-005056bba0e0"
                    }
                },
                "uuid": "bafe9b9f-db81-11e8-bd46-005056bba0e0",
                "name": "node1",
            },
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/bafe9b9f-db81-11e8-bd46-005056bba0e0"
                    }
                },
                "uuid": "bafe9b9f-db81-11e8-bd46-005056bba0e0",
                "name": "node1",
            },
            "port": {
                "node": {"name": "node1"},
                "uuid": "300c1ae3-db82-11e8-bd46-005056bba0e0",
                "name": "0a",
                "_links": {
                    "self": {
                        "href": "/api/network/fc/ports/300c1ae3-db82-11e8-bd46-005056bba0e0"
                    }
                },
            },
            "home_port": {
                "node": {"name": "node1"},
                "uuid": "300c1ae3-db82-11e8-bd46-005056bba0e0",
                "name": "0a",
                "_links": {
                    "self": {
                        "href": "/api/network/fc/ports/300c1ae3-db82-11e8-bd46-005056bba0e0"
                    }
                },
            },
        },
        "wwnn": "20:00:00:50:56:bb:a0:e0",
        "name": "lif1",
        "_links": {
            "self": {
                "href": "/api/network/fc/interfaces/f6045b92-dec7-11e8-a733-005056bba0e0"
            }
        },
    }
)

```
</div>
</div>

---
### Creating an FC interface using the port UUID to identify the location
This example uses the `return_records` query parameter to retrieve the newly created FC interface in the POST response.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FcInterface()
    resource.svm = {"name": "svm3"}
    resource.name = "lif2"
    resource.location = {"home_port": {"uuid": "24bb636a-db83-11e8-9a49-005056bb1ec6"}}
    resource.data_protocol = "fc_nvme"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
FcInterface(
    {
        "enabled": True,
        "port_address": "612e202b",
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/a5060466-dbab-11e8-bd46-005056bba0e0"}
            },
            "uuid": "a5060466-dbab-11e8-bd46-005056bba0e0",
            "name": "svm3",
        },
        "data_protocol": "fc_nvme",
        "uuid": "cdeb5591-dec9-11e8-a733-005056bba0e0",
        "wwpn": "20:05:00:50:56:bb:a0:e0",
        "state": "down",
        "location": {
            "home_node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/e85aa147-db83-11e8-9a48-005056bb1ec6"
                    }
                },
                "uuid": "e85aa147-db83-11e8-9a48-005056bb1ec6",
                "name": "node3",
            },
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/e85aa147-db83-11e8-9a48-005056bb1ec6"
                    }
                },
                "uuid": "e85aa147-db83-11e8-9a48-005056bb1ec6",
                "name": "node3",
            },
            "port": {
                "node": {"name": "node3"},
                "uuid": "24bb636a-db83-11e8-9a49-005056bb1ec6",
                "name": "1b",
                "_links": {
                    "self": {
                        "href": "/api/network/fc/ports/24bb636a-db83-11e8-9a49-005056bb1ec6"
                    }
                },
            },
            "home_port": {
                "node": {"name": "node3"},
                "uuid": "24bb636a-db83-11e8-9a49-005056bb1ec6",
                "name": "1b",
                "_links": {
                    "self": {
                        "href": "/api/network/fc/ports/24bb636a-db83-11e8-9a49-005056bb1ec6"
                    }
                },
            },
        },
        "wwnn": "20:02:00:50:56:bb:a0:e0",
        "name": "lif2",
        "_links": {
            "self": {
                "href": "/api/network/fc/interfaces/cdeb5591-dec9-11e8-a733-005056bba0e0"
            }
        },
    }
)

```
</div>
</div>

---
### Retrieving all properties for all FC interfaces
This example uses the `fields` query parameter to retrieve all properties.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(FcInterface.get_collection(fields="*")))

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    FcInterface(
        {
            "enabled": True,
            "port_address": "612e202b",
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/a5060466-dbab-11e8-bd46-005056bba0e0"
                    }
                },
                "uuid": "a5060466-dbab-11e8-bd46-005056bba0e0",
                "name": "svm3",
            },
            "data_protocol": "fc_nvme",
            "uuid": "cdeb5591-dec9-11e8-a733-005056bba0e0",
            "wwpn": "20:05:00:50:56:bb:a0:e0",
            "state": "down",
            "location": {
                "home_node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/e85aa147-db83-11e8-9a48-005056bb1ec6"
                        }
                    },
                    "uuid": "e85aa147-db83-11e8-9a48-005056bb1ec6",
                    "name": "node3",
                },
                "node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/e85aa147-db83-11e8-9a48-005056bb1ec6"
                        }
                    },
                    "uuid": "e85aa147-db83-11e8-9a48-005056bb1ec6",
                    "name": "node3",
                },
                "port": {
                    "node": {"name": "node3"},
                    "uuid": "24bb636a-db83-11e8-9a49-005056bb1ec6",
                    "name": "1b",
                    "_links": {
                        "self": {
                            "href": "/api/network/fc/ports/24bb636a-db83-11e8-9a49-005056bb1ec6"
                        }
                    },
                },
                "home_port": {
                    "node": {"name": "node3"},
                    "uuid": "24bb636a-db83-11e8-9a49-005056bb1ec6",
                    "name": "1b",
                    "_links": {
                        "self": {
                            "href": "/api/network/fc/ports/24bb636a-db83-11e8-9a49-005056bb1ec6"
                        }
                    },
                },
            },
            "wwnn": "20:02:00:50:56:bb:a0:e0",
            "name": "lif2",
            "_links": {
                "self": {
                    "href": "/api/network/fc/interfaces/cdeb5591-dec9-11e8-a733-005056bba0e0"
                }
            },
        }
    ),
    FcInterface(
        {
            "enabled": True,
            "port_address": "9da2cb1",
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/cf300f5c-db83-11e8-bd46-005056bba0e0"
                    }
                },
                "uuid": "cf300f5c-db83-11e8-bd46-005056bba0e0",
                "name": "svm1",
            },
            "data_protocol": "fcp",
            "uuid": "f6045b92-dec7-11e8-a733-005056bba0e0",
            "wwpn": "20:04:00:50:56:bb:a0:e0",
            "state": "down",
            "location": {
                "home_node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/bafe9b9f-db81-11e8-bd46-005056bba0e0"
                        }
                    },
                    "uuid": "bafe9b9f-db81-11e8-bd46-005056bba0e0",
                    "name": "node1",
                },
                "node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/bafe9b9f-db81-11e8-bd46-005056bba0e0"
                        }
                    },
                    "uuid": "bafe9b9f-db81-11e8-bd46-005056bba0e0",
                    "name": "node1",
                },
                "port": {
                    "node": {"name": "node1"},
                    "uuid": "300c1ae3-db82-11e8-bd46-005056bba0e0",
                    "name": "0a",
                    "_links": {
                        "self": {
                            "href": "/api/network/fc/ports/300c1ae3-db82-11e8-bd46-005056bba0e0"
                        }
                    },
                },
                "home_port": {
                    "node": {"name": "node1"},
                    "uuid": "300c1ae3-db82-11e8-bd46-005056bba0e0",
                    "name": "0a",
                    "_links": {
                        "self": {
                            "href": "/api/network/fc/ports/300c1ae3-db82-11e8-bd46-005056bba0e0"
                        }
                    },
                },
            },
            "wwnn": "20:00:00:50:56:bb:a0:e0",
            "name": "lif1",
            "_links": {
                "self": {
                    "href": "/api/network/fc/interfaces/f6045b92-dec7-11e8-a733-005056bba0e0"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving a list of selected FC interfaces
This example uses property query parameters to retrieve FC interfaces configured for the FC Protocol that are set to _up_.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(FcInterface.get_collection(data_protocol="fcp", state="up")))

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
[
    FcInterface(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/cf300f5c-db83-11e8-bd46-005056bba0e0"
                    }
                },
                "uuid": "cf300f5c-db83-11e8-bd46-005056bba0e0",
                "name": "svm1",
            },
            "data_protocol": "fcp",
            "uuid": "f6045b92-dec7-11e8-a733-005056bba0e0",
            "state": "up",
            "name": "lif1",
            "_links": {
                "self": {
                    "href": "/api/network/fc/interfaces/f6045b92-dec7-11e8-a733-005056bba0e0"
                }
            },
        }
    )
]

```
</div>
</div>

---
### Retrieving a specific FC interface
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FcInterface(uuid="cdeb5591-dec9-11e8-a733-005056bba0e0")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
FcInterface(
    {
        "enabled": True,
        "port_address": "612e202b",
        "statistics": {
            "iops_raw": {"total": 3, "write": 0, "read": 0, "other": 3},
            "status": "ok",
            "timestamp": "2019-04-09T05:50:42+00:00",
            "latency_raw": {"total": 38298, "write": 0, "read": 0, "other": 38298},
            "throughput_raw": {"total": 0, "write": 0, "read": 0},
        },
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/a5060466-dbab-11e8-bd46-005056bba0e0"}
            },
            "uuid": "a5060466-dbab-11e8-bd46-005056bba0e0",
            "name": "svm3",
        },
        "data_protocol": "fc_nvme",
        "uuid": "cdeb5591-dec9-11e8-a733-005056bba0e0",
        "wwpn": "20:05:00:50:56:bb:a0:e0",
        "state": "down",
        "metric": {
            "status": "ok",
            "timestamp": "2019-04-09T05:50:15+00:00",
            "latency": {"total": 0, "write": 0, "read": 0, "other": 0},
            "throughput": {"total": 0, "write": 0, "read": 0},
            "duration": "PT15S",
            "iops": {"total": 0, "write": 0, "read": 0, "other": 0},
        },
        "location": {
            "home_node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/e85aa147-db83-11e8-9a48-005056bb1ec6"
                    }
                },
                "uuid": "e85aa147-db83-11e8-9a48-005056bb1ec6",
                "name": "node3",
            },
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/e85aa147-db83-11e8-9a48-005056bb1ec6"
                    }
                },
                "uuid": "e85aa147-db83-11e8-9a48-005056bb1ec6",
                "name": "node3",
            },
            "port": {
                "node": {"name": "node3"},
                "uuid": "24bb636a-db83-11e8-9a49-005056bb1ec6",
                "name": "1b",
                "_links": {
                    "self": {
                        "href": "/api/network/fc/ports/24bb636a-db83-11e8-9a49-005056bb1ec6"
                    }
                },
            },
            "home_port": {
                "node": {"name": "node3"},
                "uuid": "24bb636a-db83-11e8-9a49-005056bb1ec6",
                "name": "1b",
                "_links": {
                    "self": {
                        "href": "/api/network/fc/ports/24bb636a-db83-11e8-9a49-005056bb1ec6"
                    }
                },
            },
        },
        "wwnn": "20:02:00:50:56:bb:a0:e0",
        "name": "lif2",
        "_links": {
            "self": {
                "href": "/api/network/fc/interfaces/cdeb5591-dec9-11e8-a733-005056bba0e0"
            }
        },
    }
)

```
</div>
</div>

---
## Disabling an FC interface
When updating certain properties or deleting an FC interface, the interface must first be disabled using the following:
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FcInterface(uuid="f6045b92-dec7-11e8-a733-005056bba0e0")
    resource.enabled = False
    resource.patch()

```

---
### Moving an FC interface to a new node and port
To move an FC interface to another node or port, the destination FC port must be specified in a PATCH request. Either the port UUID or node and port names can be used to identify the port.<br/>
Note that only FC interfaces configured for the FC Protocol can be moved. FC interfaces configured for NVMe/FC cannot be moved. The interface must also be set to the disabled state before being moved.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FcInterface(uuid="f6045b92-dec7-11e8-a733-005056bba0e0")
    resource.location = {"home_port": {"uuid": "a1dc7aa5-db83-11e8-9ef7-005056bbbbcc"}}
    resource.patch()

```

---
### Deleting an FC interface
The FC interface must be disabled before being deleted.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FcInterface(uuid="f6045b92-dec7-11e8-a733-005056bba0e0")
    resource.delete()

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


__all__ = ["FcInterface", "FcInterfaceSchema"]
__pdoc__ = {
    "FcInterfaceSchema.resource": False,
    "FcInterface.fc_interface_show": False,
    "FcInterface.fc_interface_create": False,
    "FcInterface.fc_interface_modify": False,
    "FcInterface.fc_interface_delete": False,
}


class FcInterfaceSchema(ResourceSchema):
    """The fields of the FcInterface object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the fc_interface. """

    comment = fields.Str(
        data_key="comment",
    )
    r""" A user configurable comment. Optional in POST; valid in PATCH. To clear a prior comment, set the property to an empty string in PATCH. """

    data_protocol = fields.Str(
        data_key="data_protocol",
        validate=enum_validation(['fcp', 'fc_nvme']),
    )
    r""" The data protocol for which the FC interface is configured. Required in POST.


Valid choices:

* fcp
* fc_nvme """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" The administrative state of the FC interface. The FC interface can be disabled to block all FC communication with the SVM through this interface. Optional in POST and PATCH; defaults to _true_ (enabled) in POST. """

    location = fields.Nested("netapp_ontap.models.fc_interface_location.FcInterfaceLocationSchema", data_key="location", unknown=EXCLUDE)
    r""" The location field of the fc_interface. """

    metric = fields.Nested("netapp_ontap.models.performance_metric_reduced_throughput.PerformanceMetricReducedThroughputSchema", data_key="metric", unknown=EXCLUDE)
    r""" The metric field of the fc_interface. """

    name = fields.Str(
        data_key="name",
    )
    r""" The name of the FC interface. Required in POST; optional in PATCH.


Example: fc_lif1 """

    port_address = fields.Str(
        data_key="port_address",
    )
    r""" The port address of the FC interface. Each FC port in an FC switched fabric has its own unique FC port address for routing purposes. The FC port address is assigned by a switch in the fabric when that port logs in to the fabric. This property refers to the address given by a switch to the FC interface when the SVM performs a port login (PLOGI).<br/>
This is useful for obtaining statistics and diagnostic information from FC switches.<br/>
This is a hexadecimal encoded numeric value.


Example: 5060F """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['up', 'down']),
    )
    r""" The current operational state of the FC interface. The state is set to _down_ if the interface is not enabled.<br/>
If the node hosting the port is down or unavailable, no state value is returned.


Valid choices:

* up
* down """

    statistics = fields.Nested("netapp_ontap.models.performance_metric_raw_reduced_throughput.PerformanceMetricRawReducedThroughputSchema", data_key="statistics", unknown=EXCLUDE)
    r""" The statistics field of the fc_interface. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the fc_interface. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The unique identifier of the FC interface. Required in the URL.


Example: bce9827d-4d8f-60af-c771-6e8e9af2c6f0 """

    wwnn = fields.Str(
        data_key="wwnn",
    )
    r""" The world wide node name (WWNN) of the FC interface SVM. The WWNN is generated by ONTAP when Fibre Channel Protocol or the NVMe service is created for the FC interface SVM.


Example: 20:00:00:50:56:b4:13:01 """

    wwpn = fields.Str(
        data_key="wwpn",
    )
    r""" The world wide port name (WWPN) of the FC interface. The WWPN is generated by ONTAP when the FC interface is created.


Example: 20:00:00:50:56:b4:13:a8 """

    @property
    def resource(self):
        return FcInterface

    gettable_fields = [
        "links",
        "comment",
        "data_protocol",
        "enabled",
        "location",
        "metric",
        "name",
        "port_address",
        "state",
        "statistics",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
        "wwnn",
        "wwpn",
    ]
    """links,comment,data_protocol,enabled,location,metric,name,port_address,state,statistics,svm.links,svm.name,svm.uuid,uuid,wwnn,wwpn,"""

    patchable_fields = [
        "comment",
        "enabled",
        "location",
        "name",
        "svm.name",
        "svm.uuid",
    ]
    """comment,enabled,location,name,svm.name,svm.uuid,"""

    postable_fields = [
        "comment",
        "data_protocol",
        "enabled",
        "location",
        "name",
        "svm.name",
        "svm.uuid",
    ]
    """comment,data_protocol,enabled,location,name,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FcInterface.get_collection(fields=field)]
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
            raise NetAppRestError("FcInterface modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FcInterface(Resource):
    r""" A Fibre Channel (FC) interface is the logical endpoint for FC network connections to an SVM. An FC interface provides FC access to storage within the interface SVM using either Fibre Channel Protocol or NVMe over Fibre Channel (NVMe/FC).<br/>
An FC interface is created on an FC port which is located on a cluster node. The FC port must be specified to identify the location of the interface for a POST or PATCH operation that relocates an interface. You can identify the port by supplying either the node and port names or the port UUID. """

    _schema = FcInterfaceSchema
    _path = "/api/network/fc/interfaces"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves FC interfaces.
### Related ONTAP commands
* `network interface show`
* `vserver fcp interface show`
### Learn more
* [`DOC /network/fc/interfaces`](#docs-networking-network_fc_interfaces)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fc interface show")
        def fc_interface_show(
            fields: List[Choices.define(["comment", "data_protocol", "enabled", "name", "port_address", "state", "uuid", "wwnn", "wwpn", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of FcInterface resources

            Args:
                comment: A user configurable comment. Optional in POST; valid in PATCH. To clear a prior comment, set the property to an empty string in PATCH. 
                data_protocol: The data protocol for which the FC interface is configured. Required in POST. 
                enabled: The administrative state of the FC interface. The FC interface can be disabled to block all FC communication with the SVM through this interface. Optional in POST and PATCH; defaults to _true_ (enabled) in POST. 
                name: The name of the FC interface. Required in POST; optional in PATCH. 
                port_address: The port address of the FC interface. Each FC port in an FC switched fabric has its own unique FC port address for routing purposes. The FC port address is assigned by a switch in the fabric when that port logs in to the fabric. This property refers to the address given by a switch to the FC interface when the SVM performs a port login (PLOGI).<br/> This is useful for obtaining statistics and diagnostic information from FC switches.<br/> This is a hexadecimal encoded numeric value. 
                state: The current operational state of the FC interface. The state is set to _down_ if the interface is not enabled.<br/> If the node hosting the port is down or unavailable, no state value is returned. 
                uuid: The unique identifier of the FC interface. Required in the URL. 
                wwnn: The world wide node name (WWNN) of the FC interface SVM. The WWNN is generated by ONTAP when Fibre Channel Protocol or the NVMe service is created for the FC interface SVM. 
                wwpn: The world wide port name (WWPN) of the FC interface. The WWPN is generated by ONTAP when the FC interface is created. 
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if data_protocol is not None:
                kwargs["data_protocol"] = data_protocol
            if enabled is not None:
                kwargs["enabled"] = enabled
            if name is not None:
                kwargs["name"] = name
            if port_address is not None:
                kwargs["port_address"] = port_address
            if state is not None:
                kwargs["state"] = state
            if uuid is not None:
                kwargs["uuid"] = uuid
            if wwnn is not None:
                kwargs["wwnn"] = wwnn
            if wwpn is not None:
                kwargs["wwpn"] = wwpn
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return FcInterface.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all FcInterface resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["FcInterface"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an FC interface.
### Related ONTAP commands
* `network interface modify`
### Learn more
* [`DOC /network/fc/interfaces`](#docs-networking-network_fc_interfaces)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["FcInterface"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["FcInterface"], NetAppResponse]:
        r"""Creates an FC interface.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the FC interface.
* `name` - Name of the FC interface.
* `location.port.uuid` or both `location.port.name` and `location.port.node.name` - FC port on which to create the FC interface.
* `data_protocol` - Data protocol for the FC interface.
### Default property values
If not specified in POST, the following default property values are assigned.
* `enabled` - _true_
### Related ONTAP commands
* `network interface create`
### Learn more
* [`DOC /network/fc/interfaces`](#docs-networking-network_fc_interfaces)
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
        records: Iterable["FcInterface"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an FC interface.
### Related ONTAP commands
* `network interface delete`
### Learn more
* [`DOC /network/fc/interfaces`](#docs-networking-network_fc_interfaces)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves FC interfaces.
### Related ONTAP commands
* `network interface show`
* `vserver fcp interface show`
### Learn more
* [`DOC /network/fc/interfaces`](#docs-networking-network_fc_interfaces)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an FC interface.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `network interface show`
* `vserver fcp interface show`
### Learn more
* [`DOC /network/fc/interfaces`](#docs-networking-network_fc_interfaces)
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
        r"""Creates an FC interface.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the FC interface.
* `name` - Name of the FC interface.
* `location.port.uuid` or both `location.port.name` and `location.port.node.name` - FC port on which to create the FC interface.
* `data_protocol` - Data protocol for the FC interface.
### Default property values
If not specified in POST, the following default property values are assigned.
* `enabled` - _true_
### Related ONTAP commands
* `network interface create`
### Learn more
* [`DOC /network/fc/interfaces`](#docs-networking-network_fc_interfaces)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fc interface create")
        async def fc_interface_create(
        ) -> ResourceTable:
            """Create an instance of a FcInterface resource

            Args:
                links: 
                comment: A user configurable comment. Optional in POST; valid in PATCH. To clear a prior comment, set the property to an empty string in PATCH. 
                data_protocol: The data protocol for which the FC interface is configured. Required in POST. 
                enabled: The administrative state of the FC interface. The FC interface can be disabled to block all FC communication with the SVM through this interface. Optional in POST and PATCH; defaults to _true_ (enabled) in POST. 
                location: 
                metric: 
                name: The name of the FC interface. Required in POST; optional in PATCH. 
                port_address: The port address of the FC interface. Each FC port in an FC switched fabric has its own unique FC port address for routing purposes. The FC port address is assigned by a switch in the fabric when that port logs in to the fabric. This property refers to the address given by a switch to the FC interface when the SVM performs a port login (PLOGI).<br/> This is useful for obtaining statistics and diagnostic information from FC switches.<br/> This is a hexadecimal encoded numeric value. 
                state: The current operational state of the FC interface. The state is set to _down_ if the interface is not enabled.<br/> If the node hosting the port is down or unavailable, no state value is returned. 
                statistics: 
                svm: 
                uuid: The unique identifier of the FC interface. Required in the URL. 
                wwnn: The world wide node name (WWNN) of the FC interface SVM. The WWNN is generated by ONTAP when Fibre Channel Protocol or the NVMe service is created for the FC interface SVM. 
                wwpn: The world wide port name (WWPN) of the FC interface. The WWPN is generated by ONTAP when the FC interface is created. 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if comment is not None:
                kwargs["comment"] = comment
            if data_protocol is not None:
                kwargs["data_protocol"] = data_protocol
            if enabled is not None:
                kwargs["enabled"] = enabled
            if location is not None:
                kwargs["location"] = location
            if metric is not None:
                kwargs["metric"] = metric
            if name is not None:
                kwargs["name"] = name
            if port_address is not None:
                kwargs["port_address"] = port_address
            if state is not None:
                kwargs["state"] = state
            if statistics is not None:
                kwargs["statistics"] = statistics
            if svm is not None:
                kwargs["svm"] = svm
            if uuid is not None:
                kwargs["uuid"] = uuid
            if wwnn is not None:
                kwargs["wwnn"] = wwnn
            if wwpn is not None:
                kwargs["wwpn"] = wwpn

            resource = FcInterface(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create FcInterface: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an FC interface.
### Related ONTAP commands
* `network interface modify`
### Learn more
* [`DOC /network/fc/interfaces`](#docs-networking-network_fc_interfaces)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fc interface modify")
        async def fc_interface_modify(
        ) -> ResourceTable:
            """Modify an instance of a FcInterface resource

            Args:
                comment: A user configurable comment. Optional in POST; valid in PATCH. To clear a prior comment, set the property to an empty string in PATCH. 
                query_comment: A user configurable comment. Optional in POST; valid in PATCH. To clear a prior comment, set the property to an empty string in PATCH. 
                data_protocol: The data protocol for which the FC interface is configured. Required in POST. 
                query_data_protocol: The data protocol for which the FC interface is configured. Required in POST. 
                enabled: The administrative state of the FC interface. The FC interface can be disabled to block all FC communication with the SVM through this interface. Optional in POST and PATCH; defaults to _true_ (enabled) in POST. 
                query_enabled: The administrative state of the FC interface. The FC interface can be disabled to block all FC communication with the SVM through this interface. Optional in POST and PATCH; defaults to _true_ (enabled) in POST. 
                name: The name of the FC interface. Required in POST; optional in PATCH. 
                query_name: The name of the FC interface. Required in POST; optional in PATCH. 
                port_address: The port address of the FC interface. Each FC port in an FC switched fabric has its own unique FC port address for routing purposes. The FC port address is assigned by a switch in the fabric when that port logs in to the fabric. This property refers to the address given by a switch to the FC interface when the SVM performs a port login (PLOGI).<br/> This is useful for obtaining statistics and diagnostic information from FC switches.<br/> This is a hexadecimal encoded numeric value. 
                query_port_address: The port address of the FC interface. Each FC port in an FC switched fabric has its own unique FC port address for routing purposes. The FC port address is assigned by a switch in the fabric when that port logs in to the fabric. This property refers to the address given by a switch to the FC interface when the SVM performs a port login (PLOGI).<br/> This is useful for obtaining statistics and diagnostic information from FC switches.<br/> This is a hexadecimal encoded numeric value. 
                state: The current operational state of the FC interface. The state is set to _down_ if the interface is not enabled.<br/> If the node hosting the port is down or unavailable, no state value is returned. 
                query_state: The current operational state of the FC interface. The state is set to _down_ if the interface is not enabled.<br/> If the node hosting the port is down or unavailable, no state value is returned. 
                uuid: The unique identifier of the FC interface. Required in the URL. 
                query_uuid: The unique identifier of the FC interface. Required in the URL. 
                wwnn: The world wide node name (WWNN) of the FC interface SVM. The WWNN is generated by ONTAP when Fibre Channel Protocol or the NVMe service is created for the FC interface SVM. 
                query_wwnn: The world wide node name (WWNN) of the FC interface SVM. The WWNN is generated by ONTAP when Fibre Channel Protocol or the NVMe service is created for the FC interface SVM. 
                wwpn: The world wide port name (WWPN) of the FC interface. The WWPN is generated by ONTAP when the FC interface is created. 
                query_wwpn: The world wide port name (WWPN) of the FC interface. The WWPN is generated by ONTAP when the FC interface is created. 
            """

            kwargs = {}
            changes = {}
            if query_comment is not None:
                kwargs["comment"] = query_comment
            if query_data_protocol is not None:
                kwargs["data_protocol"] = query_data_protocol
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_name is not None:
                kwargs["name"] = query_name
            if query_port_address is not None:
                kwargs["port_address"] = query_port_address
            if query_state is not None:
                kwargs["state"] = query_state
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid
            if query_wwnn is not None:
                kwargs["wwnn"] = query_wwnn
            if query_wwpn is not None:
                kwargs["wwpn"] = query_wwpn

            if comment is not None:
                changes["comment"] = comment
            if data_protocol is not None:
                changes["data_protocol"] = data_protocol
            if enabled is not None:
                changes["enabled"] = enabled
            if name is not None:
                changes["name"] = name
            if port_address is not None:
                changes["port_address"] = port_address
            if state is not None:
                changes["state"] = state
            if uuid is not None:
                changes["uuid"] = uuid
            if wwnn is not None:
                changes["wwnn"] = wwnn
            if wwpn is not None:
                changes["wwpn"] = wwpn

            if hasattr(FcInterface, "find"):
                resource = FcInterface.find(
                    **kwargs
                )
            else:
                resource = FcInterface()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify FcInterface: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an FC interface.
### Related ONTAP commands
* `network interface delete`
### Learn more
* [`DOC /network/fc/interfaces`](#docs-networking-network_fc_interfaces)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fc interface delete")
        async def fc_interface_delete(
        ) -> None:
            """Delete an instance of a FcInterface resource

            Args:
                comment: A user configurable comment. Optional in POST; valid in PATCH. To clear a prior comment, set the property to an empty string in PATCH. 
                data_protocol: The data protocol for which the FC interface is configured. Required in POST. 
                enabled: The administrative state of the FC interface. The FC interface can be disabled to block all FC communication with the SVM through this interface. Optional in POST and PATCH; defaults to _true_ (enabled) in POST. 
                name: The name of the FC interface. Required in POST; optional in PATCH. 
                port_address: The port address of the FC interface. Each FC port in an FC switched fabric has its own unique FC port address for routing purposes. The FC port address is assigned by a switch in the fabric when that port logs in to the fabric. This property refers to the address given by a switch to the FC interface when the SVM performs a port login (PLOGI).<br/> This is useful for obtaining statistics and diagnostic information from FC switches.<br/> This is a hexadecimal encoded numeric value. 
                state: The current operational state of the FC interface. The state is set to _down_ if the interface is not enabled.<br/> If the node hosting the port is down or unavailable, no state value is returned. 
                uuid: The unique identifier of the FC interface. Required in the URL. 
                wwnn: The world wide node name (WWNN) of the FC interface SVM. The WWNN is generated by ONTAP when Fibre Channel Protocol or the NVMe service is created for the FC interface SVM. 
                wwpn: The world wide port name (WWPN) of the FC interface. The WWPN is generated by ONTAP when the FC interface is created. 
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if data_protocol is not None:
                kwargs["data_protocol"] = data_protocol
            if enabled is not None:
                kwargs["enabled"] = enabled
            if name is not None:
                kwargs["name"] = name
            if port_address is not None:
                kwargs["port_address"] = port_address
            if state is not None:
                kwargs["state"] = state
            if uuid is not None:
                kwargs["uuid"] = uuid
            if wwnn is not None:
                kwargs["wwnn"] = wwnn
            if wwpn is not None:
                kwargs["wwpn"] = wwpn

            if hasattr(FcInterface, "find"):
                resource = FcInterface.find(
                    **kwargs
                )
            else:
                resource = FcInterface()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete FcInterface: %s" % err)


