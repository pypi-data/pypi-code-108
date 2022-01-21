r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
NVMe interfaces are network interfaces configured to support an NVMe over Fabrics (NVMe-oF) protocol. The NVMe interfaces are Fibre Channel (FC) interfaces supporting an NVMe-oF data protocol. Regardless of the underlying physical and data protocol, NVMe interfaces are treated equally for host-side application configuration. This endpoint provides a consolidated view of all NVMe interfaces for the purpose of configuring host-side applications.<br/>
The NVMe interfaces REST API provides NVMe-specific information about network interfaces configured to support an NVMe-oF protocol.<br/>
NVMe interfaces must be created using the protocol-specific endpoints for FC interfaces. See [`POST /network/fc/interfaces`](#/networking/fc_interface_create). After creation, the interfaces are available via this interface.
## Examples
### Retrieving summary information for all NVMe interfaces
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(NvmeInterface.get_collection()))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    NvmeInterface(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/013e2c44-0d30-11e9-a684-005056bbdb14"
                    }
                },
                "uuid": "013e2c44-0d30-11e9-a684-005056bbdb14",
                "name": "svm1",
            },
            "uuid": "74d69872-0d30-11e9-a684-005056bbdb14",
            "name": "nvme1",
            "_links": {
                "self": {
                    "href": "/api/protocols/nvme/interfaces/74d69872-0d30-11e9-a684-005056bbdb14"
                }
            },
        }
    ),
    NvmeInterface(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/013e2c44-0d30-11e9-a684-005056bbdb14"
                    }
                },
                "uuid": "013e2c44-0d30-11e9-a684-005056bbdb14",
                "name": "svm1",
            },
            "uuid": "77ded991-0d30-11e9-a684-005056bbdb14",
            "name": "nvme2",
            "_links": {
                "self": {
                    "href": "/api/protocols/nvme/interfaces/77ded991-0d30-11e9-a684-005056bbdb14"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving detailed information for a specific NVMe interface
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeInterface(uuid="77ded991-0d30-11e9-a684-005056bbdb14")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
NvmeInterface(
    {
        "fc_interface": {
            "wwnn": "20:03:00:50:56:bb:db:14",
            "port": {
                "node": {"name": "node1"},
                "uuid": "081ec491-0d2f-11e9-a684-005056bbdb14",
                "name": "1a",
                "_links": {
                    "self": {
                        "href": "/api/network/fc/ports/081ec491-0d2f-11e9-a684-005056bbdb14"
                    }
                },
            },
            "wwpn": "20:05:00:50:56:bb:db:14",
            "_links": {
                "self": {
                    "href": "/api/network/fc/interfaces/77ded991-0d30-11e9-a684-005056bbdb14"
                }
            },
        },
        "enabled": True,
        "transport_address": "nn-0x2003005056bbdb14:pn-0x2005005056bbdb14",
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/013e2c44-0d30-11e9-a684-005056bbdb14"}
            },
            "uuid": "013e2c44-0d30-11e9-a684-005056bbdb14",
            "name": "svm1",
        },
        "uuid": "77ded991-0d30-11e9-a684-005056bbdb14",
        "node": {
            "_links": {
                "self": {
                    "href": "/api/cluster/nodes/cd4d47fd-0d2e-11e9-a684-005056bbdb14"
                }
            },
            "uuid": "cd4d47fd-0d2e-11e9-a684-005056bbdb14",
            "name": "node1",
        },
        "name": "nvme2",
        "_links": {
            "self": {
                "href": "/api/protocols/nvme/interfaces/77ded991-0d30-11e9-a684-005056bbdb14"
            }
        },
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


__all__ = ["NvmeInterface", "NvmeInterfaceSchema"]
__pdoc__ = {
    "NvmeInterfaceSchema.resource": False,
    "NvmeInterface.nvme_interface_show": False,
    "NvmeInterface.nvme_interface_create": False,
    "NvmeInterface.nvme_interface_modify": False,
    "NvmeInterface.nvme_interface_delete": False,
}


class NvmeInterfaceSchema(ResourceSchema):
    """The fields of the NvmeInterface object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the nvme_interface. """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" The administrative state of the NVMe interface. """

    fc_interface = fields.Nested("netapp_ontap.models.nvme_interface_fc_interface.NvmeInterfaceFcInterfaceSchema", data_key="fc_interface", unknown=EXCLUDE)
    r""" The fc_interface field of the nvme_interface. """

    interface_type = fields.Str(
        data_key="interface_type",
        validate=enum_validation(['fc_interface', 'ip_interface']),
    )
    r""" The underlying interface type of the NVMe interface. This property identifies which of _fc_interface_ and _ip_interface_ will be further populated.


Valid choices:

* fc_interface
* ip_interface """

    ip_interface = fields.Nested("netapp_ontap.models.nvme_interface_ip_interface.NvmeInterfaceIpInterfaceSchema", data_key="ip_interface", unknown=EXCLUDE)
    r""" The ip_interface field of the nvme_interface. """

    name = fields.Str(
        data_key="name",
    )
    r""" The name of the NVMe interface.


Example: lif1 """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the nvme_interface. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the nvme_interface. """

    transport_address = fields.Str(
        data_key="transport_address",
    )
    r""" The transport address of the NVMe interface.


Example: nn-0x200a00a0989062da:pn-0x200100a0989062da """

    transport_protocols = fields.List(fields.Str, data_key="transport_protocols")
    r""" The transport protocols supported by the NVMe interface. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The unique identifier of the NVMe interface.


Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return NvmeInterface

    gettable_fields = [
        "links",
        "enabled",
        "fc_interface",
        "interface_type",
        "ip_interface",
        "name",
        "node.links",
        "node.name",
        "node.uuid",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "transport_address",
        "transport_protocols",
        "uuid",
    ]
    """links,enabled,fc_interface,interface_type,ip_interface,name,node.links,node.name,node.uuid,svm.links,svm.name,svm.uuid,transport_address,transport_protocols,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NvmeInterface.get_collection(fields=field)]
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
            raise NetAppRestError("NvmeInterface modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NvmeInterface(Resource):
    r""" NVMe interfaces are network interfaces configured to support an NVMe over Fabrics (NVMe-oF) protocol. The NVMe interfaces are Fibre Channel interfaces supporting an NVMe-oF data protocol. Regardless of the underlying physical and data protocol, NVMe interfaces are treated equally for host-side application configuration. This endpoint provides a consolidated view of all NVMe interfaces for the purpose of configuring host-side applications.<br/>
NVMe interfaces must be created using the protocol-specific endpoints for Fibre Channel interfaces. See [`POST /network/fc/interfaces`](#/networking/fc_interface_create). After creation, the interfaces are available via this interface. """

    _schema = NvmeInterfaceSchema
    _path = "/api/protocols/nvme/interfaces"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves NVMe interfaces.
### Related ONTAP commands
* `vserver nvme show-interface`
### Learn more
* [`DOC /protocols/nvme/interfaces`](#docs-NVMe-protocols_nvme_interfaces)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme interface show")
        def nvme_interface_show(
            fields: List[Choices.define(["enabled", "interface_type", "name", "transport_address", "transport_protocols", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of NvmeInterface resources

            Args:
                enabled: The administrative state of the NVMe interface. 
                interface_type: The underlying interface type of the NVMe interface. This property identifies which of _fc_interface_ and _ip_interface_ will be further populated. 
                name: The name of the NVMe interface. 
                transport_address: The transport address of the NVMe interface. 
                transport_protocols: The transport protocols supported by the NVMe interface. 
                uuid: The unique identifier of the NVMe interface. 
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if interface_type is not None:
                kwargs["interface_type"] = interface_type
            if name is not None:
                kwargs["name"] = name
            if transport_address is not None:
                kwargs["transport_address"] = transport_address
            if transport_protocols is not None:
                kwargs["transport_protocols"] = transport_protocols
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return NvmeInterface.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NvmeInterface resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves NVMe interfaces.
### Related ONTAP commands
* `vserver nvme show-interface`
### Learn more
* [`DOC /protocols/nvme/interfaces`](#docs-NVMe-protocols_nvme_interfaces)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an NVMe interface.
### Related ONTAP commands
* `vserver nvme show-interface`
### Learn more
* [`DOC /protocols/nvme/interfaces`](#docs-NVMe-protocols_nvme_interfaces)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)





