r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
A portset is a collection of Fibre Channel Protocol and/or iSCSI network interfaces from the portset's SVM.<br/>
Portsets are used to limit the network interfaces through which an initiator can connect to mapped LUNs. When a portset is bound to an initiator group (igroup), and the initiator group is mapped to a LUN, the initiators of the initiator group can only reach the LUN through the network interfaces in the portset.<br/>
Portsets are not recommended for new configurations. With modern releases of ONTAP, it is recommended to use multiple SVMs and initiator groups with no bound portset to load balance applications over multiple ports on a node. Selective LUN mapping will automatically limit the number of visible paths to a LUN from the client host to those required for efficient access and high availability. The REST portset API is primarily intended for legacy use.<br/>
The portset REST API allows you to create, delete, and discover portsets, and to add and remove network interaces from portsets.<br/>
A portset can be bound to one or more initiator groups. An initiator group (igroup) can be bound to at most one portset.<br/>
When a portset is created, the `protocol` property is used to restrict member network interfaces to Fibre Channel Procotol (_fcp_), iSCSI (_iscsi_), or both (_mixed_).<br/>
Zero or more network interfaces can be supplied when the portset is created. After creation, network interfaces can be added to or removed from the portset using the `/protocols/san/portsets/{portset.uuid}/interfaces` endpoint. See [`POST /protocols/san/portsets/{portset.uuid}/interfaces`](#/SAN/portset_interface_create) and [`DELETE /protocols/san/portsets/{portset.uuid}/interfaces/{name}`](#/SAN/portset_interface_delete) for more details.<br/>
## Examples
### Creating a portset with no network interfaces
The example portset uses the default `mixed` protocol. Note that the `return_records` query parameter is used to obtain the newly created portset in the response.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Portset

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Portset()
    resource.svm = {"name": "svm1"}
    resource.name = "portset1"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
Portset(
    {
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/31484775-1e23-11eb-b2a8-005056bb3521"}
            },
            "uuid": "31484775-1e23-11eb-b2a8-005056bb3521",
            "name": "svm1",
        },
        "uuid": "5d7b1dfa-1ed7-11eb-8b0f-005056bb3521",
        "protocol": "mixed",
        "name": "portset1",
        "_links": {
            "self": {
                "href": "/api/protocols/san/portsets/5d7b1dfa-1ed7-11eb-8b0f-005056bb3521"
            }
        },
    }
)

```
</div>
</div>

---
### Creating an iSCSI portset with two network interfaces
Note that the `return_records` query parameter is used to obtain the newly created portset in the response.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Portset

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Portset()
    resource.svm = {"name": "svm1"}
    resource.name = "portset2"
    resource.protocol = "iscsi"
    resource.interfaces = [{"ip": {"name": "lif1"}}, {"ip": {"name": "lif2"}}]
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
Portset(
    {
        "interfaces": [
            {
                "ip": {
                    "_links": {
                        "self": {
                            "href": "/api/network/ip/interfaces/f37bfb01-1e2a-11eb-b2a8-005056bb3521"
                        }
                    },
                    "ip": {"address": "192.168.1.100"},
                    "uuid": "f37bfb01-1e2a-11eb-b2a8-005056bb3521",
                    "name": "lif1",
                },
                "uuid": "f37bfb01-1e2a-11eb-b2a8-005056bb3521",
                "_links": {
                    "self": {
                        "href": "/api/protocols/san/portsets/816c0d49-1ed7-11eb-8b0f-005056bb3521/interfaces/f37bfb01-1e2a-11eb-b2a8-005056bb3521"
                    }
                },
            },
            {
                "ip": {
                    "_links": {
                        "self": {
                            "href": "/api/network/ip/interfaces/f92178e7-1e2a-11eb-b2a8-005056bb3521"
                        }
                    },
                    "ip": {"address": "192.168.1.101"},
                    "uuid": "f92178e7-1e2a-11eb-b2a8-005056bb3521",
                    "name": "lif2",
                },
                "uuid": "f92178e7-1e2a-11eb-b2a8-005056bb3521",
                "_links": {
                    "self": {
                        "href": "/api/protocols/san/portsets/816c0d49-1ed7-11eb-8b0f-005056bb3521/interfaces/f92178e7-1e2a-11eb-b2a8-005056bb3521"
                    }
                },
            },
        ],
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/31484775-1e23-11eb-b2a8-005056bb3521"}
            },
            "uuid": "31484775-1e23-11eb-b2a8-005056bb3521",
            "name": "svm1",
        },
        "uuid": "816c0d49-1ed7-11eb-8b0f-005056bb3521",
        "protocol": "iscsi",
        "name": "portset2",
        "_links": {
            "self": {
                "href": "/api/protocols/san/portsets/816c0d49-1ed7-11eb-8b0f-005056bb3521"
            }
        },
    }
)

```
</div>
</div>

---
### Retrieving a summary of all portsets
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Portset

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(Portset.get_collection()))

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    Portset(
        {
            "uuid": "5d7b1dfa-1ed7-11eb-8b0f-005056bb3521",
            "name": "portset1",
            "_links": {
                "self": {
                    "href": "/api/protocols/san/portsets/5d7b1dfa-1ed7-11eb-8b0f-005056bb3521"
                }
            },
        }
    ),
    Portset(
        {
            "uuid": "816c0d49-1ed7-11eb-8b0f-005056bb3521",
            "name": "portset2",
            "_links": {
                "self": {
                    "href": "/api/protocols/san/portsets/816c0d49-1ed7-11eb-8b0f-005056bb3521"
                }
            },
        }
    ),
    Portset(
        {
            "uuid": "b716b4d2-1ed7-11eb-8b0f-005056bb3521",
            "name": "portset3",
            "_links": {
                "self": {
                    "href": "/api/protocols/san/portsets/b716b4d2-1ed7-11eb-8b0f-005056bb3521"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving details for a specific portset
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Portset

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Portset(uuid="b716b4d2-1ed7-11eb-8b0f-005056bb3521")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
Portset(
    {
        "interfaces": [
            {
                "fc": {
                    "uuid": "164eb052-1e2b-11eb-b2a8-005056bb3521",
                    "wwpn": "20:01:00:50:56:bb:35:21",
                    "name": "lif5",
                    "_links": {
                        "self": {
                            "href": "/api/network/fc/interfaces/164eb052-1e2b-11eb-b2a8-005056bb3521"
                        }
                    },
                },
                "uuid": "164eb052-1e2b-11eb-b2a8-005056bb3521",
                "_links": {
                    "self": {
                        "href": "/api/protocols/san/portsets/b716b4d2-1ed7-11eb-8b0f-005056bb3521/interfaces/164eb052-1e2b-11eb-b2a8-005056bb3521"
                    }
                },
            },
            {
                "fc": {
                    "uuid": "197ba2b7-1e2b-11eb-b2a8-005056bb3521",
                    "wwpn": "20:02:00:50:56:bb:35:21",
                    "name": "lif6",
                    "_links": {
                        "self": {
                            "href": "/api/network/fc/interfaces/197ba2b7-1e2b-11eb-b2a8-005056bb3521"
                        }
                    },
                },
                "uuid": "197ba2b7-1e2b-11eb-b2a8-005056bb3521",
                "_links": {
                    "self": {
                        "href": "/api/protocols/san/portsets/b716b4d2-1ed7-11eb-8b0f-005056bb3521/interfaces/197ba2b7-1e2b-11eb-b2a8-005056bb3521"
                    }
                },
            },
        ],
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/31484775-1e23-11eb-b2a8-005056bb3521"}
            },
            "uuid": "31484775-1e23-11eb-b2a8-005056bb3521",
            "name": "svm1",
        },
        "uuid": "b716b4d2-1ed7-11eb-8b0f-005056bb3521",
        "protocol": "fcp",
        "name": "portset3",
        "_links": {
            "self": {
                "href": "/api/protocols/san/portsets/b716b4d2-1ed7-11eb-8b0f-005056bb3521"
            }
        },
    }
)

```
</div>
</div>

---
### Deleting a portset
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Portset

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Portset(uuid="b716b4d2-1ed7-11eb-8b0f-005056bb3521")
    resource.delete()

```

---
### Adding a network interface to a portset
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import PortsetInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = PortsetInterface("5d7b1dfa-1ed7-11eb-8b0f-005056bb3521")
    resource.fc = {"name": "lif4"}
    resource.post(hydrate=True)
    print(resource)

```

---
### Adding multiple network interfaces to a portset in a single call
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import PortsetInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = PortsetInterface("5d7b1dfa-1ed7-11eb-8b0f-005056bb3521")
    resource.records = [
        {"ip": {"name": "lif1"}},
        {"ip": {"name": "lif2"}},
        {"fc": {"name": "lif5"}},
    ]
    resource.post(hydrate=True)
    print(resource)

```

---
### Removing a network interface from a portset
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import PortsetInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = PortsetInterface(
        "5d7b1dfa-1ed7-11eb-8b0f-005056bb3521",
        uuid="f92178e7-1e2a-11eb-b2a8-005056bb3521",
    )
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


__all__ = ["Portset", "PortsetSchema"]
__pdoc__ = {
    "PortsetSchema.resource": False,
    "Portset.portset_show": False,
    "Portset.portset_create": False,
    "Portset.portset_modify": False,
    "Portset.portset_delete": False,
}


class PortsetSchema(ResourceSchema):
    """The fields of the Portset object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the portset. """

    igroups = fields.List(fields.Nested("netapp_ontap.resources.igroup.IgroupSchema", unknown=EXCLUDE), data_key="igroups")
    r""" An array initiator groups to which the portset is bound. """

    interfaces = fields.List(fields.Nested("netapp_ontap.models.portset_interface_no_records.PortsetInterfaceNoRecordsSchema", unknown=EXCLUDE), data_key="interfaces")
    r""" An array of network interfaces that are members of the portset. These are the only network interfaces through which the initiators of a bound igroup can access mapped LUNs.<br/>
Zero or more network interfaces can be supplied when the portset is created. After creation, network interfaces can be added or removed from the portset using the `/protocols/san/portsets/{portset.uuid}/interfaces` endpoint. See [`POST /protocols/san/portsets/{portset.uuid}/interfaces`](#/SAN/portset_interface_create) and [`DELETE /protocols/san/portsets/{portset.uuid}/interfaces/{uuid}`](#/SAN/portset_interface_delete) for more details. """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=1, maximum=96),
    )
    r""" The name of the portset. Required in POST.<br/>
The name of a portset cannot be changed after creation.


Example: portset1 """

    protocol = fields.Str(
        data_key="protocol",
        validate=enum_validation(['fcp', 'iscsi', 'mixed']),
    )
    r""" The protocols supported by the portset. This restricts the type of network interfaces that can be added to the portset. Optional in POST; if not supplied, this defaults to _mixed_.<br/>
The protocol of a portset cannot be changed after creation.


Valid choices:

* fcp
* iscsi
* mixed """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the portset. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The unique identifier for a portset.


Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return Portset

    gettable_fields = [
        "links",
        "igroups.links",
        "igroups.name",
        "igroups.uuid",
        "interfaces",
        "name",
        "protocol",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
    ]
    """links,igroups.links,igroups.name,igroups.uuid,interfaces,name,protocol,svm.links,svm.name,svm.uuid,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "interfaces",
        "name",
        "protocol",
        "svm.name",
        "svm.uuid",
    ]
    """interfaces,name,protocol,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Portset.get_collection(fields=field)]
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
            raise NetAppRestError("Portset modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Portset(Resource):
    """Allows interaction with Portset objects on the host"""

    _schema = PortsetSchema
    _path = "/api/protocols/san/portsets"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves portsets.
### Related ONTAP commands
* `lun portset show`
### Learn more
* [`DOC /protocols/san/portsets`](#docs-SAN-protocols_san_portsets)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="portset show")
        def portset_show(
            fields: List[Choices.define(["name", "protocol", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of Portset resources

            Args:
                name: The name of the portset. Required in POST.<br/> The name of a portset cannot be changed after creation. 
                protocol: The protocols supported by the portset. This restricts the type of network interfaces that can be added to the portset. Optional in POST; if not supplied, this defaults to _mixed_.<br/> The protocol of a portset cannot be changed after creation. 
                uuid: The unique identifier for a portset. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if protocol is not None:
                kwargs["protocol"] = protocol
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return Portset.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Portset resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["Portset"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["Portset"], NetAppResponse]:
        r"""Creates a portset.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the portset.
* `name` - Name of the portset.
### Recommended optional properties
* `protocol` - The network protocol of the interfaces in the portset.
* `interfaces` - Network interfaces to include in the portset. This property can be used to create the portset and populate it with network interfaces in a single request.
### Default property values
If not specified in POST, the following default property values are assigned.
* `protocol` - _mixed_ - Data protocol of the portset's network interfaces.
### Related ONTAP commands
* `lun portset create`
### Learn more
* [`DOC /protocols/san/portsets`](#docs-SAN-protocols_san_portsets)
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
        records: Iterable["Portset"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a portset.
### Related ONTAP commands
* `lun portset delete`
### Learn more
* [`DOC /protocols/san/portsets`](#docs-SAN-protocols_san_portsets)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves portsets.
### Related ONTAP commands
* `lun portset show`
### Learn more
* [`DOC /protocols/san/portsets`](#docs-SAN-protocols_san_portsets)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a portset.
### Related ONTAP commands
* `lun portset show`
### Learn more
* [`DOC /protocols/san/portsets`](#docs-SAN-protocols_san_portsets)
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
        r"""Creates a portset.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the portset.
* `name` - Name of the portset.
### Recommended optional properties
* `protocol` - The network protocol of the interfaces in the portset.
* `interfaces` - Network interfaces to include in the portset. This property can be used to create the portset and populate it with network interfaces in a single request.
### Default property values
If not specified in POST, the following default property values are assigned.
* `protocol` - _mixed_ - Data protocol of the portset's network interfaces.
### Related ONTAP commands
* `lun portset create`
### Learn more
* [`DOC /protocols/san/portsets`](#docs-SAN-protocols_san_portsets)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="portset create")
        async def portset_create(
        ) -> ResourceTable:
            """Create an instance of a Portset resource

            Args:
                links: 
                igroups: An array initiator groups to which the portset is bound. 
                interfaces: An array of network interfaces that are members of the portset. These are the only network interfaces through which the initiators of a bound igroup can access mapped LUNs.<br/> Zero or more network interfaces can be supplied when the portset is created. After creation, network interfaces can be added or removed from the portset using the `/protocols/san/portsets/{portset.uuid}/interfaces` endpoint. See [`POST /protocols/san/portsets/{portset.uuid}/interfaces`](#/SAN/portset_interface_create) and [`DELETE /protocols/san/portsets/{portset.uuid}/interfaces/{uuid}`](#/SAN/portset_interface_delete) for more details. 
                name: The name of the portset. Required in POST.<br/> The name of a portset cannot be changed after creation. 
                protocol: The protocols supported by the portset. This restricts the type of network interfaces that can be added to the portset. Optional in POST; if not supplied, this defaults to _mixed_.<br/> The protocol of a portset cannot be changed after creation. 
                svm: 
                uuid: The unique identifier for a portset. 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if igroups is not None:
                kwargs["igroups"] = igroups
            if interfaces is not None:
                kwargs["interfaces"] = interfaces
            if name is not None:
                kwargs["name"] = name
            if protocol is not None:
                kwargs["protocol"] = protocol
            if svm is not None:
                kwargs["svm"] = svm
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = Portset(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create Portset: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a portset.
### Related ONTAP commands
* `lun portset delete`
### Learn more
* [`DOC /protocols/san/portsets`](#docs-SAN-protocols_san_portsets)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="portset delete")
        async def portset_delete(
        ) -> None:
            """Delete an instance of a Portset resource

            Args:
                name: The name of the portset. Required in POST.<br/> The name of a portset cannot be changed after creation. 
                protocol: The protocols supported by the portset. This restricts the type of network interfaces that can be added to the portset. Optional in POST; if not supplied, this defaults to _mixed_.<br/> The protocol of a portset cannot be changed after creation. 
                uuid: The unique identifier for a portset. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if protocol is not None:
                kwargs["protocol"] = protocol
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(Portset, "find"):
                resource = Portset.find(
                    **kwargs
                )
            else:
                resource = Portset()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete Portset: %s" % err)


