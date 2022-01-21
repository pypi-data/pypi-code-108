r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
You can use this API to retrieve and display relevant information pertaining to MetroCluster interconnect status. The ```/cluster/metrocluster/interconnects``` endpoint returns a list of all the interconnects in MetroCluster and their status. Each individual interconnect can be queried individually using the ```/cluster/metrocluster/interconnects/{node.uuid}/{partner_type}/{adapter}``` endpoint. You can also use this API to modify relevant information related to MetroCluster interconnect. These include address, netmask, and gateway. Modify a MetroCluster interconnect using the ```/cluster/metrocluster/interconnects/{node.uuid}/{partner_type}/{adapter}``` endpoint.
####
---
### Examples
### Retrieving MetroCluster interconnects
```
GET https://<mgmt-ip>/api/cluster/metrocluster/interconnects
{
    "records": [
        {
            "node": {
                "name": "cluster1_01",
                "uuid": "6fead8fe-8d81-11e9-b5a9-005056826931",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/6fead8fe-8d81-11e9-b5a9-005056826931"
                    }
                }
            },
            "partner_type": "ha",
            "adapter": "e0f",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/interconnects/6fead8fe-8d81-11e9-b5a9-005056826931/ha/e0f"
                }
            }
        },
        {
            "node": {
                "name": "cluster1_01",
                "uuid": "6fead8fe-8d81-11e9-b5a9-005056826931",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/6fead8fe-8d81-11e9-b5a9-005056826931"
                    }
                }
            },
            "partner_type": "ha",
            "adapter": "e0g",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/interconnects/6fead8fe-8d81-11e9-b5a9-005056826931/ha/e0g"
                }
            }
        },
        {
            "node": {
                "name": "cluster1_01",
                "uuid": "6fead8fe-8d81-11e9-b5a9-005056826931",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/6fead8fe-8d81-11e9-b5a9-005056826931"
                    }
                }
            },
            "partner_type": "dr",
            "adapter": "e0f",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/interconnects/6fead8fe-8d81-11e9-b5a9-005056826931/dr/e0f"
                }
            }
        },
        {
            "node": {
                "name": "cluster1_01",
                "uuid": "6fead8fe-8d81-11e9-b5a9-005056826931",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/6fead8fe-8d81-11e9-b5a9-005056826931"
                    }
                }
            },
            "partner_type": "dr",
            "adapter": "e0g",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/interconnects/6fead8fe-8d81-11e9-b5a9-005056826931/dr/e0g"
                }
            }
        },
        {
            "node": {
                "name": "cluster1_01",
                "uuid": "6fead8fe-8d81-11e9-b5a9-005056826931",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/6fead8fe-8d81-11e9-b5a9-005056826931"
                    }
                }
            },
            "partner_type": "aux",
            "adapter": "e0f",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/interconnects/6fead8fe-8d81-11e9-b5a9-005056826931/aux/e0f"
                }
            }
        },
        {
            "node": {
                "name": "cluster1_01",
                "uuid": "6fead8fe-8d81-11e9-b5a9-005056826931",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/6fead8fe-8d81-11e9-b5a9-005056826931"
                    }
                }
            },
            "partner_type": "aux",
            "adapter": "e0g",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/interconnects/6fead8fe-8d81-11e9-b5a9-005056826931/aux/e0g"
                }
            }
        },
        {
            "node": {
                "name": "cluster1_02",
                "uuid": "f5435191-8d81-11e9-9d4b-00505682dc8b",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/f5435191-8d81-11e9-9d4b-00505682dc8b"
                    }
                }
            },
            "partner_type": "ha",
            "adapter": "e0f",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/interconnects/f5435191-8d81-11e9-9d4b-00505682dc8b/ha/e0f"
                }
            }
        },
        {
            "node": {
                "name": "cluster1_02",
                "uuid": "f5435191-8d81-11e9-9d4b-00505682dc8b",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/f5435191-8d81-11e9-9d4b-00505682dc8b"
                    }
                }
            },
            "partner_type": "ha",
            "adapter": "e0g",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/interconnects/f5435191-8d81-11e9-9d4b-00505682dc8b/ha/e0g"
                }
            }
        },
        {
            "node": {
                "name": "cluster1_02",
                "uuid": "f5435191-8d81-11e9-9d4b-00505682dc8b",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/f5435191-8d81-11e9-9d4b-00505682dc8b"
                    }
                }
            },
            "partner_type": "dr",
            "adapter": "e0f",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/interconnects/f5435191-8d81-11e9-9d4b-00505682dc8b/dr/e0f"
                }
            }
        },
        {
            "node": {
                "name": "cluster1_02",
                "uuid": "f5435191-8d81-11e9-9d4b-00505682dc8b",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/f5435191-8d81-11e9-9d4b-00505682dc8b"
                    }
                }
            },
            "partner_type": "dr",
            "adapter": "e0g",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/interconnects/f5435191-8d81-11e9-9d4b-00505682dc8b/dr/e0g"
                }
            }
        },
        {
            "node": {
                "name": "cluster1_02",
                "uuid": "f5435191-8d81-11e9-9d4b-00505682dc8b",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/f5435191-8d81-11e9-9d4b-00505682dc8b"
                    }
                }
            },
            "partner_type": "aux",
            "adapter": "e0f",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/interconnects/f5435191-8d81-11e9-9d4b-00505682dc8b/aux/e0f"
                }
            }
        },
        {
            "node": {
                "name": "cluster1_02",
                "uuid": "f5435191-8d81-11e9-9d4b-00505682dc8b",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/f5435191-8d81-11e9-9d4b-00505682dc8b"
                    }
                }
            },
            "partner_type": "aux",
            "adapter": "e0g",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/interconnects/f5435191-8d81-11e9-9d4b-00505682dc8b/aux/e0g"
                }
            }
        }
    ],
    "num_records": 12,
    "_links": {
        "self": {
            "href": "/api/cluster/metrocluster/interconnects"
        }
    }
}
```
### Retrieves information about a specific MetroCluster interconnect
```
https://<mgmt-ip>/api/cluster/metrocluster/interconnects/774b4fbc-86f9-11e9-9051-005056825c71/aux/e0f
{
    "node": {
        "name": "cluster1_01",
        "uuid": "46147363-9857-11e9-9a55-005056828eb9",
        "_links": {
            "self": {
                "href": "/api/cluster/nodes/46147363-9857-11e9-9a55-005056828eb9"
            }
        }
    },
    "partner_type": "ha",
    "adapter": "e0f",
    "state": "up",
    "type": "iwarp",
    "_links": {
        "self": {
            "href": "/api/cluster/metrocluster/interconnects/46147363-9857-11e9-9a55-005056828eb9/ha/e0f"
        }
    }
}
```
### This example shows how to modify the network address assigned to the home port. Fields required: address.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import MetroclusterInterconnect

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = MetroclusterInterconnect(
        adapter="e0g",
        partner_type="ha",
        **{"node.uuid": "3e1bfd38-ffd2-11eb-bcb7-005056aceaa9"}
    )
    resource.interfaces = [{"address": "1.2.3.4"}]
    resource.patch()

```

#### PATCH Response
```
HTTP/1.1 200 OK
Cache-Control: no-cache,no-store,must-revalidate
Connection: close
Date: Fri, 20 Aug 2021 21:58:36 GMT
Server: libzapid-httpd
Content-Length: 3
Content-Type: application/hal+json
X-Content-Type-Options: nosniff
{
}
```
### This example shows how to modify the netmask assigned to the interface. Be sure to change to a valid subnet. Fields required: netmask.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import MetroclusterInterconnect

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = MetroclusterInterconnect(
        adapter="e0g",
        partner_type="ha",
        **{"node.uuid": "3e1bfd38-ffd2-11eb-bcb7-005056aceaa9"}
    )
    resource.interfaces = [{"netmask": "2.2.2.2"}]
    resource.patch()

```

#### PATCH Response
```
HTTP/1.1 200 OK
Cache-Control: no-cache,no-store,must-revalidate
Connection: close
Date: Fri, 20 Aug 2021 22:11:35 GMT
Server: libzapid-httpd
Content-Length: 3
Content-Type: application/hal+json
X-Content-Type-Options: nosniff
{
}
```
### This example shows how to modify the gateway assigned to the interface. Please make sure to update it on the switch/router first. Assuming it is a new one, the only thing to consider is the IP address and the new gateway must be in the same subnet. Fields required: gateway.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import MetroclusterInterconnect

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = MetroclusterInterconnect(
        adapter="e0g",
        partner_type="ha",
        **{"node.uuid": "3e1bfd38-ffd2-11eb-bcb7-005056aceaa9"}
    )
    resource.interfaces = [{"gateway": "1.2.3.4"}]
    resource.patch()

```

#### PATCH Response
```
HTTP/1.1 200 OK
Cache-Control: no-cache,no-store,must-revalidate
Connection: close
Date: Fri, 20 Aug 2021 22:11:35 GMT
Server: libzapid-httpd
Content-Length: 3
Content-Type: application/hal+json
X-Content-Type-Options: nosniff
{
}
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


__all__ = ["MetroclusterInterconnect", "MetroclusterInterconnectSchema"]
__pdoc__ = {
    "MetroclusterInterconnectSchema.resource": False,
    "MetroclusterInterconnect.metrocluster_interconnect_show": False,
    "MetroclusterInterconnect.metrocluster_interconnect_create": False,
    "MetroclusterInterconnect.metrocluster_interconnect_modify": False,
    "MetroclusterInterconnect.metrocluster_interconnect_delete": False,
}


class MetroclusterInterconnectSchema(ResourceSchema):
    """The fields of the MetroclusterInterconnect object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the metrocluster_interconnect. """

    adapter = fields.Str(
        data_key="adapter",
    )
    r""" Adapter """

    interfaces = fields.List(fields.Nested("netapp_ontap.models.ip_interface_and_gateway.IpInterfaceAndGatewaySchema", unknown=EXCLUDE), data_key="interfaces")
    r""" List of objects which contain interface information such as its IP address, netmask and gateway. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the metrocluster_interconnect. """

    partner_type = fields.Str(
        data_key="partner_type",
        validate=enum_validation(['aux', 'dr', 'ha']),
    )
    r""" Partner type

Valid choices:

* aux
* dr
* ha """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['down', 'up']),
    )
    r""" Adapter status

Valid choices:

* down
* up """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['roce', 'iwarp', 'unknown']),
    )
    r""" Adapter type

Valid choices:

* roce
* iwarp
* unknown """

    vlan_id = Size(
        data_key="vlan_id",
        validate=integer_validation(minimum=10, maximum=4095),
    )
    r""" VLAN ID """

    @property
    def resource(self):
        return MetroclusterInterconnect

    gettable_fields = [
        "links",
        "adapter",
        "interfaces",
        "node.links",
        "node.name",
        "node.uuid",
        "partner_type",
        "state",
        "type",
        "vlan_id",
    ]
    """links,adapter,interfaces,node.links,node.name,node.uuid,partner_type,state,type,vlan_id,"""

    patchable_fields = [
        "interfaces",
        "node.name",
        "node.uuid",
    ]
    """interfaces,node.name,node.uuid,"""

    postable_fields = [
        "interfaces",
        "node.name",
        "node.uuid",
    ]
    """interfaces,node.name,node.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in MetroclusterInterconnect.get_collection(fields=field)]
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
            raise NetAppRestError("MetroclusterInterconnect modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class MetroclusterInterconnect(Resource):
    r""" Data for a MetroCluster interconnect. REST: /api/cluster/metrocluster/interconnects """

    _schema = MetroclusterInterconnectSchema
    _path = "/api/cluster/metrocluster/interconnects"
    _keys = ["node.uuid", "partner_type", "adapter"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a list of interconnect adapter information for nodes in the MetroCluster.
### Related ONTAP Commands
* `metrocluster interconnect show`
### Learn more
* [`DOC /cluster/metrocluster/interconnects`](#docs-cluster-cluster_metrocluster_interconnects)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="metrocluster interconnect show")
        def metrocluster_interconnect_show(
            fields: List[Choices.define(["adapter", "partner_type", "state", "type", "vlan_id", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of MetroclusterInterconnect resources

            Args:
                adapter: Adapter
                partner_type: Partner type
                state: Adapter status
                type: Adapter type
                vlan_id: VLAN ID
            """

            kwargs = {}
            if adapter is not None:
                kwargs["adapter"] = adapter
            if partner_type is not None:
                kwargs["partner_type"] = partner_type
            if state is not None:
                kwargs["state"] = state
            if type is not None:
                kwargs["type"] = type
            if vlan_id is not None:
                kwargs["vlan_id"] = vlan_id
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return MetroclusterInterconnect.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all MetroclusterInterconnect resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["MetroclusterInterconnect"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a MetroCluster interconnect interface.
### Related ONTAP commands * `metrocluster configuration-settings interface modify`
### Learn more
* [`DOC /cluster/metrocluster/interconnects`](#docs-cluster-cluster_metrocluster_interconnects)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)



    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a list of interconnect adapter information for nodes in the MetroCluster.
### Related ONTAP Commands
* `metrocluster interconnect show`
### Learn more
* [`DOC /cluster/metrocluster/interconnects`](#docs-cluster-cluster_metrocluster_interconnects)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves information about a MetroCluster Interconnect for a specific partner type and adapter.
### Related ONTAP Commands
* `metrocluster interconnect show`

### Learn more
* [`DOC /cluster/metrocluster/interconnects`](#docs-cluster-cluster_metrocluster_interconnects)"""
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
        r"""Updates a MetroCluster interconnect interface.
### Related ONTAP commands * `metrocluster configuration-settings interface modify`
### Learn more
* [`DOC /cluster/metrocluster/interconnects`](#docs-cluster-cluster_metrocluster_interconnects)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="metrocluster interconnect modify")
        async def metrocluster_interconnect_modify(
        ) -> ResourceTable:
            """Modify an instance of a MetroclusterInterconnect resource

            Args:
                adapter: Adapter
                query_adapter: Adapter
                partner_type: Partner type
                query_partner_type: Partner type
                state: Adapter status
                query_state: Adapter status
                type: Adapter type
                query_type: Adapter type
                vlan_id: VLAN ID
                query_vlan_id: VLAN ID
            """

            kwargs = {}
            changes = {}
            if query_adapter is not None:
                kwargs["adapter"] = query_adapter
            if query_partner_type is not None:
                kwargs["partner_type"] = query_partner_type
            if query_state is not None:
                kwargs["state"] = query_state
            if query_type is not None:
                kwargs["type"] = query_type
            if query_vlan_id is not None:
                kwargs["vlan_id"] = query_vlan_id

            if adapter is not None:
                changes["adapter"] = adapter
            if partner_type is not None:
                changes["partner_type"] = partner_type
            if state is not None:
                changes["state"] = state
            if type is not None:
                changes["type"] = type
            if vlan_id is not None:
                changes["vlan_id"] = vlan_id

            if hasattr(MetroclusterInterconnect, "find"):
                resource = MetroclusterInterconnect.find(
                    **kwargs
                )
            else:
                resource = MetroclusterInterconnect()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify MetroclusterInterconnect: %s" % err)



