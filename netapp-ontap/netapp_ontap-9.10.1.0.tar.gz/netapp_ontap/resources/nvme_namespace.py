r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
An NVMe namespace is a collection of addressable logical blocks presented to hosts connected to the storage virtual machine using the NVMe over Fabrics protocol.<br/>
The NVMe namespace REST API allows you to create, update, delete and discover NVMe namespaces.<br/>
In ONTAP, an NVMe namespace is located within a volume. Optionally, it can be located within a qtree in a volume.<br/>
An NVMe namespace is created to a specified size using thin or thick provisioning as determined by the volume on which it is created. NVMe namespaces support being cloned. An NVMe namespace cannot be renamed, resized, or moved to a different volume. NVMe namespaces do not support the assignment of a QoS policy for performance management, but a QoS policy can be assigned to the volume containing the namespace. See the NVMe namespace object model to learn more about each of the properties supported by the NVMe namespace REST API.<br/>
An NVMe namespace must be mapped to an NVMe subsystem to grant access to the subsystem's hosts. Hosts can then access the NVMe namespace and perform I/O using the NVMe over Fabrics protocol.
## Performance monitoring
Performance of an NVMe namespace can be monitored by observing the `metric.*` and `statistics.*` properties. These properties show the performance of an NVMe namespace in terms of IOPS, latency, and throughput. The `metric.*` properties denote an average, whereas `statistics.*` properties denote a real-time monotonically increasing value aggregated across all nodes.
## Examples
### Creating an NVMe namespace
This example creates a 300 gigabyte NVMe namespace, with 4096-byte blocks, in SVM _svm1_, volume _vol1_, configured for use by _linux_ hosts. The `return_records` query parameter is used to retrieve properties of the newly created NVMe namespace in the POST response.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeNamespace

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeNamespace()
    resource.svm = {"name": "svm1"}
    resource.os_type = "linux"
    resource.space = {"block_size": "4096", "size": "300G"}
    resource.name = "/vol/vol1/namespace1"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
NvmeNamespace(
    {
        "os_type": "linux",
        "enabled": True,
        "status": {"state": "online", "container_state": "online", "read_only": False},
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/6bf967fd-2a1c-11e9-b682-005056bbc17d"}
            },
            "uuid": "6bf967fd-2a1c-11e9-b682-005056bbc17d",
            "name": "svm1",
        },
        "uuid": "dccdc3e6-cf4e-498f-bec6-f7897f945669",
        "space": {
            "size": 322122547200,
            "guarantee": {"reserved": False, "requested": False},
            "block_size": 4096,
            "used": 0,
        },
        "location": {
            "volume": {
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/71cd0dba-2a1c-11e9-b682-005056bbc17d"
                    }
                },
                "uuid": "71cd0dba-2a1c-11e9-b682-005056bbc17d",
                "name": "vol1",
            },
            "namespace": "namespace1",
        },
        "name": "/vol/vol1/namespace1",
        "_links": {
            "self": {
                "href": "/api/storage/namespaces/dccdc3e6-cf4e-498f-bec6-f7897f945669"
            }
        },
    }
)

```
</div>
</div>

---
### Updating an NVMe namespace comment
This example sets the `comment` property of an NVMe namespace.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeNamespace

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeNamespace(uuid="dccdc3e6-cf4e-498f-bec6-f7897f945669")
    resource.comment = "Data for the research department."
    resource.patch()

```

### Updating the size of an NVMe namespace
This example increases the size of an NVMe namespace.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeNamespace

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeNamespace(uuid="dccdc3e6-cf4e-498f-bec6-f7897f945669")
    resource.space = {"size": "1073741824"}
    resource.patch()

```

---
### Retrieving NVMe namespaces
This example retrieves summary information for all online NVMe namespaces in SVM _svm1_. The `svm.name` and `status.state` query parameters are to find the desired NVMe namespaces.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeNamespace

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            NvmeNamespace.get_collection(
                **{"svm.name": "svm1", "status.state": "online"}
            )
        )
    )

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
[
    NvmeNamespace(
        {
            "status": {"state": "online"},
            "svm": {"name": "svm1"},
            "uuid": "5c254d22-96a6-42ac-aad8-0cd9ebd126b6",
            "name": "/vol/vol1/namespace2",
            "_links": {
                "self": {
                    "href": "/api/storage/namespaces/5c254d22-96a6-42ac-aad8-0cd9ebd126b6"
                }
            },
        }
    ),
    NvmeNamespace(
        {
            "status": {"state": "online"},
            "svm": {"name": "svm1"},
            "uuid": "dccdc3e6-cf4e-498f-bec6-f7897f945669",
            "name": "/vol/vol1/namespace1",
            "_links": {
                "self": {
                    "href": "/api/storage/namespaces/dccdc3e6-cf4e-498f-bec6-f7897f945669"
                }
            },
        }
    ),
    NvmeNamespace(
        {
            "status": {"state": "online"},
            "svm": {"name": "svm1"},
            "uuid": "be732687-20cf-47d2-a0e2-2a989d15661d",
            "name": "/vol/vol2/namespace3",
            "_links": {
                "self": {
                    "href": "/api/storage/namespaces/be732687-20cf-47d2-a0e2-2a989d15661d"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving details for a specific NVMe namespace
In this example, the `fields` query parameter is used to request all fields, including advanced fields, that would not otherwise be returned by default for the NVMe namespace.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeNamespace

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeNamespace(uuid="dccdc3e6-cf4e-498f-bec6-f7897f945669")
    resource.get(fields="**")
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
NvmeNamespace(
    {
        "os_type": "linux",
        "enabled": True,
        "status": {
            "state": "online",
            "mapped": True,
            "container_state": "online",
            "read_only": False,
        },
        "statistics": {
            "iops_raw": {"total": 3, "write": 0, "read": 0, "other": 3},
            "status": "ok",
            "timestamp": "2019-04-09T05:50:42+00:00",
            "latency_raw": {"total": 38298, "write": 0, "read": 0, "other": 38298},
            "throughput_raw": {"total": 0, "write": 0, "read": 0},
        },
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/6bf967fd-2a1c-11e9-b682-005056bbc17d"}
            },
            "uuid": "6bf967fd-2a1c-11e9-b682-005056bbc17d",
            "name": "svm1",
        },
        "uuid": "dccdc3e6-cf4e-498f-bec6-f7897f945669",
        "auto_delete": False,
        "space": {
            "size": 322122547200,
            "guarantee": {"reserved": False, "requested": False},
            "block_size": 4096,
            "used": 0,
        },
        "comment": "Data for the research department.",
        "metric": {
            "status": "ok",
            "timestamp": "2019-04-09T05:50:15+00:00",
            "latency": {"total": 0, "write": 0, "read": 0, "other": 0},
            "throughput": {"total": 0, "write": 0, "read": 0},
            "duration": "PT15S",
            "iops": {"total": 0, "write": 0, "read": 0, "other": 0},
        },
        "subsystem_map": {
            "anagrpid": "00000001h",
            "subsystem": {
                "uuid": "01f17d05-2be9-11e9-bed2-005056bbc17d",
                "name": "subsystem1",
                "_links": {
                    "self": {
                        "href": "/api/protocols/nvme/subsystems/01f17d05-2be9-11e9-bed2-005056bbc17d"
                    }
                },
            },
            "nsid": "00000001h",
            "_links": {
                "self": {
                    "href": "/api/protocols/nvme/subsystem-maps/dccdc3e6-cf4e-498f-bec6-f7897f945669/01f17d05-2be9-11e9-bed2-005056bbc17d"
                }
            },
        },
        "location": {
            "volume": {
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/71cd0dba-2a1c-11e9-b682-005056bbc17d"
                    }
                },
                "uuid": "71cd0dba-2a1c-11e9-b682-005056bbc17d",
                "name": "vol1",
            },
            "namespace": "namespace1",
        },
        "name": "/vol/vol1/namespace1",
        "_links": {
            "self": {
                "href": "/api/storage/namespaces/dccdc3e6-cf4e-498f-bec6-f7897f945669?fields=**"
            }
        },
    }
)

```
</div>
</div>

---
## Cloning NVMe namespaces
A clone of an NVMe namespace is an independent "copy" of the namespace that shares unchanged data blocks with the original. As blocks of the source and clone are modified, unique blocks are written for each. NVMe namespace clones can be created quickly and consume very little space initially. They can be created for the purpose of back-up, or to replicate data for multiple consumers.<br/>
An NVMe namespace clone can also be set to auto-delete by setting the `auto_delete` property. If the namespace's volume is configured for automatic deletion, NVMe namespaces that have auto-delete enabled are deleted when a volume is nearly full to reclaim a target amount of free space in the volume.
### Creating a new NVMe namespace clone
You create an NVMe namespace clone as you create any NVMe namespace -- a POST to [`/storage/namespaces`](#/NVMe/nvme_namespace_create). Set `clone.source.uuid` or `clone.source.name` to identify the source NVMe namespace from which the clone is created. The NVMe namespace clone and its source must reside in the same volume.
<br/>
The source NVMe namespace can reside in a Snapshot copy, in which case, the `clone.source.name` field must be used to identify it. Add `/.snapshot/<snapshot_name>` to the path after the volume name to identify the Snapshot copy. For example `/vol/vol1/.snapshot/snap1/namespace1`.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeNamespace

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeNamespace()
    resource.svm = {"name": "svm1"}
    resource.name = "/vol/vol1/namespace2clone1"
    resource.clone = {"source": {"name": "/vol/vol1/namespace2"}}
    resource.post(hydrate=True)
    print(resource)

```

---
### Over-writing an existing NVMe namespace's data as a clone of another
You can over-write an existing NVMe namespace as a clone of another. You do this as a PATCH on the NVMe namespace to overwrite -- a PATCH to [`/storage/namespaces/{uuid}`](#/NVMe/nvme_namespace_modify). Set the `clone.source.uuid` or `clone.source.name` property to identify the source NVMe namespace from which the clone data is taken. The NVMe namespace clone and its source must reside in the same volume.<br/>
When used in a PATCH, the patched NVMe namespace's data is over-written as a clone of the source and the following properties are preserved from the patched namespace unless otherwise specified as part of the PATCH: `auto_delete`, `subsystem_map`, `status.state`, and `uuid`.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeNamespace

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeNamespace(uuid="dccdc3e6-cf4e-498f-bec6-f7897f945669")
    resource.clone = {"source": {"name": "/vol/vol1/namespace2"}}
    resource.patch()

```

---
## Deleting an NVMe namespace
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeNamespace

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeNamespace(uuid="5c254d22-96a6-42ac-aad8-0cd9ebd126b6")
    resource.delete()

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


__all__ = ["NvmeNamespace", "NvmeNamespaceSchema"]
__pdoc__ = {
    "NvmeNamespaceSchema.resource": False,
    "NvmeNamespace.nvme_namespace_show": False,
    "NvmeNamespace.nvme_namespace_create": False,
    "NvmeNamespace.nvme_namespace_modify": False,
    "NvmeNamespace.nvme_namespace_delete": False,
}


class NvmeNamespaceSchema(ResourceSchema):
    """The fields of the NvmeNamespace object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the nvme_namespace. """

    auto_delete = fields.Boolean(
        data_key="auto_delete",
    )
    r""" This property marks the NVMe namespace for auto deletion when the volume containing the namespace runs out of space. This is most commonly set on namespace clones.<br/>
When set to _true_, the NVMe namespace becomes eligible for automatic deletion when the volume runs out of space. Auto deletion only occurs when the volume containing the namespace is also configured for auto deletion and free space in the volume decreases below a particular threshold.<br/>
This property is optional in POST and PATCH. The default value for a new NVMe namespace is _false_.<br/>
There is an added cost to retrieving this property's value. It is not populated for either a collection GET or an instance GET unless it is explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more. """

    clone = fields.Nested("netapp_ontap.models.nvme_namespace_clone.NvmeNamespaceCloneSchema", data_key="clone", unknown=EXCLUDE)
    r""" The clone field of the nvme_namespace. """

    comment = fields.Str(
        data_key="comment",
        validate=len_validation(minimum=0, maximum=254),
    )
    r""" A configurable comment available for use by the administrator. Valid in POST and PATCH. """

    create_time = ImpreciseDateTime(
        data_key="create_time",
    )
    r""" The time the NVMe namespace was created.

Example: 2018-06-04T19:00:00.000+0000 """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" The enabled state of the NVMe namespace. Certain error conditions cause the namespace to become disabled. If the namespace is disabled, you can check the `state` property to determine what error disabled the namespace. An NVMe namespace is enabled automatically when it is created. """

    location = fields.Nested("netapp_ontap.models.nvme_namespace_location.NvmeNamespaceLocationSchema", data_key="location", unknown=EXCLUDE)
    r""" The location field of the nvme_namespace. """

    metric = fields.Nested("netapp_ontap.models.performance_metric_reduced_throughput.PerformanceMetricReducedThroughputSchema", data_key="metric", unknown=EXCLUDE)
    r""" The metric field of the nvme_namespace. """

    name = fields.Str(
        data_key="name",
    )
    r""" The fully qualified path name of the NVMe namespace composed of a "/vol" prefix, the volume name, the (optional) qtree name and base name of the namespace. Valid in POST.<br/>
NVMe namespaces do not support rename, or movement between volumes.


Example: /vol/volume1/qtree1/namespace1 """

    os_type = fields.Str(
        data_key="os_type",
        validate=enum_validation(['aix', 'linux', 'vmware', 'windows']),
    )
    r""" The operating system type of the NVMe namespace.<br/>
Required in POST when creating an NVMe namespace that is not a clone of another. Disallowed in POST when creating a namespace clone.


Valid choices:

* aix
* linux
* vmware
* windows """

    space = fields.Nested("netapp_ontap.models.nvme_namespace_space.NvmeNamespaceSpaceSchema", data_key="space", unknown=EXCLUDE)
    r""" The space field of the nvme_namespace. """

    statistics = fields.Nested("netapp_ontap.models.performance_metric_raw_reduced_throughput.PerformanceMetricRawReducedThroughputSchema", data_key="statistics", unknown=EXCLUDE)
    r""" The statistics field of the nvme_namespace. """

    status = fields.Nested("netapp_ontap.models.nvme_namespace_status.NvmeNamespaceStatusSchema", data_key="status", unknown=EXCLUDE)
    r""" The status field of the nvme_namespace. """

    subsystem_map = fields.Nested("netapp_ontap.models.nvme_namespace_subsystem_map.NvmeNamespaceSubsystemMapSchema", data_key="subsystem_map", unknown=EXCLUDE)
    r""" The subsystem_map field of the nvme_namespace. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the nvme_namespace. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The unique identifier of the NVMe namespace.


Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return NvmeNamespace

    gettable_fields = [
        "links",
        "auto_delete",
        "comment",
        "create_time",
        "enabled",
        "location",
        "metric",
        "name",
        "os_type",
        "space",
        "statistics",
        "status",
        "subsystem_map",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
    ]
    """links,auto_delete,comment,create_time,enabled,location,metric,name,os_type,space,statistics,status,subsystem_map,svm.links,svm.name,svm.uuid,uuid,"""

    patchable_fields = [
        "auto_delete",
        "clone",
        "comment",
        "space",
        "status",
        "subsystem_map",
        "svm.name",
        "svm.uuid",
    ]
    """auto_delete,clone,comment,space,status,subsystem_map,svm.name,svm.uuid,"""

    postable_fields = [
        "auto_delete",
        "clone",
        "comment",
        "location",
        "name",
        "os_type",
        "space",
        "status",
        "subsystem_map",
        "svm.name",
        "svm.uuid",
    ]
    """auto_delete,clone,comment,location,name,os_type,space,status,subsystem_map,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NvmeNamespace.get_collection(fields=field)]
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
            raise NetAppRestError("NvmeNamespace modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NvmeNamespace(Resource):
    r""" An NVMe namespace is a collection of addressable logical blocks presented to hosts connected to the storage virtual machine using the NVMe over Fabrics protocol.<br/>
In ONTAP, an NVMe namespace is located within a volume. Optionally, it can be located within a qtree in a volume.<br/>
An NVMe namespace is created to a specified size using thin or thick provisioning as determined by the volume on which it is created. NVMe namespaces support being cloned. An NVMe namespace cannot be renamed, resized, or moved to a different volume. NVMe namespaces do not support the assignment of a QoS policy for performance management, but a QoS policy can be assigned to the volume containing the namespace. See the NVMe namespace object model to learn more about each of the properties supported by the NVMe namespace REST API.<br/>
An NVMe namespace must be mapped to an NVMe subsystem to grant access to the subsystem's hosts. Hosts can then access the NVMe namespace and perform I/O using the NVMe over Fabrics protocol. """

    _schema = NvmeNamespaceSchema
    _path = "/api/storage/namespaces"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves NVMe namespaces.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `auto_delete`
* `subsystem_map.*`
* `status.mapped`
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `vserver nvme namespace show`
* `vserver nvme subsystem map show`
### Learn more
* [`DOC /storage/namespaces`](#docs-NVMe-storage_namespaces) to learn more and examples.
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme namespace show")
        def nvme_namespace_show(
            fields: List[Choices.define(["auto_delete", "comment", "create_time", "enabled", "name", "os_type", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of NvmeNamespace resources

            Args:
                auto_delete: This property marks the NVMe namespace for auto deletion when the volume containing the namespace runs out of space. This is most commonly set on namespace clones.<br/> When set to _true_, the NVMe namespace becomes eligible for automatic deletion when the volume runs out of space. Auto deletion only occurs when the volume containing the namespace is also configured for auto deletion and free space in the volume decreases below a particular threshold.<br/> This property is optional in POST and PATCH. The default value for a new NVMe namespace is _false_.<br/> There is an added cost to retrieving this property's value. It is not populated for either a collection GET or an instance GET unless it is explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more. 
                comment: A configurable comment available for use by the administrator. Valid in POST and PATCH. 
                create_time: The time the NVMe namespace was created.
                enabled: The enabled state of the NVMe namespace. Certain error conditions cause the namespace to become disabled. If the namespace is disabled, you can check the `state` property to determine what error disabled the namespace. An NVMe namespace is enabled automatically when it is created. 
                name: The fully qualified path name of the NVMe namespace composed of a \"/vol\" prefix, the volume name, the (optional) qtree name and base name of the namespace. Valid in POST.<br/> NVMe namespaces do not support rename, or movement between volumes. 
                os_type: The operating system type of the NVMe namespace.<br/> Required in POST when creating an NVMe namespace that is not a clone of another. Disallowed in POST when creating a namespace clone. 
                uuid: The unique identifier of the NVMe namespace. 
            """

            kwargs = {}
            if auto_delete is not None:
                kwargs["auto_delete"] = auto_delete
            if comment is not None:
                kwargs["comment"] = comment
            if create_time is not None:
                kwargs["create_time"] = create_time
            if enabled is not None:
                kwargs["enabled"] = enabled
            if name is not None:
                kwargs["name"] = name
            if os_type is not None:
                kwargs["os_type"] = os_type
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return NvmeNamespace.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NvmeNamespace resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["NvmeNamespace"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an NVMe namespace.
### Related ONTAP commands
* `volume file clone autodelete`
* `vserver nvme namespace modify`
### Learn more
* [`DOC /storage/namespaces`](#docs-NVMe-storage_namespaces)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["NvmeNamespace"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["NvmeNamespace"], NetAppResponse]:
        r"""Creates an NVMe namespace.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the NVMe namespace.
* `name`, `location.volume.name` or `location.volume.uuid` - Existing volume in which to create the NVMe namespace.
* `name` or `location.namespace` - Base name for the NVMe namespace.
* `os_type` - Operating system from which the NVMe namespace will be accessed. (Not used for clones, which are created based on the `os_type` of the source NVMe namespace.)
* `space.size` - Size for the NVMe namespace. (Not used for clones, which are created based on the size of the source NVMe namespace.)
### Default property values
If not specified in POST, the following default property values are assigned:
* `auto_delete` - _false_
* `space.block_size` - _4096_ ( _512_ when 'os_type' is _vmware_ )
### Related ONTAP commands
* `volume file clone autodelete`
* `volume file clone create`
* `vserver nvme namespace create`
### Learn more
* [`DOC /storage/namespaces`](#docs-NVMe-storage_namespaces)
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
        records: Iterable["NvmeNamespace"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an NVMe namespace.
### Related ONTAP commands
* `vserver nvme namespace delete`
### Learn more
* [`DOC /storage/namespaces`](#docs-NVMe-storage_namespaces)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves NVMe namespaces.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `auto_delete`
* `subsystem_map.*`
* `status.mapped`
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `vserver nvme namespace show`
* `vserver nvme subsystem map show`
### Learn more
* [`DOC /storage/namespaces`](#docs-NVMe-storage_namespaces) to learn more and examples.
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an NVMe namespace.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `auto_delete`
* `subsystem_map.*`
* `status.mapped`
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `vserver nvme namespace show`
* `vserver nvme subsystem map show`
### Learn more
* [`DOC /storage/namespaces`](#docs-NVMe-storage_namespaces)
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
        r"""Creates an NVMe namespace.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the NVMe namespace.
* `name`, `location.volume.name` or `location.volume.uuid` - Existing volume in which to create the NVMe namespace.
* `name` or `location.namespace` - Base name for the NVMe namespace.
* `os_type` - Operating system from which the NVMe namespace will be accessed. (Not used for clones, which are created based on the `os_type` of the source NVMe namespace.)
* `space.size` - Size for the NVMe namespace. (Not used for clones, which are created based on the size of the source NVMe namespace.)
### Default property values
If not specified in POST, the following default property values are assigned:
* `auto_delete` - _false_
* `space.block_size` - _4096_ ( _512_ when 'os_type' is _vmware_ )
### Related ONTAP commands
* `volume file clone autodelete`
* `volume file clone create`
* `vserver nvme namespace create`
### Learn more
* [`DOC /storage/namespaces`](#docs-NVMe-storage_namespaces)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme namespace create")
        async def nvme_namespace_create(
        ) -> ResourceTable:
            """Create an instance of a NvmeNamespace resource

            Args:
                links: 
                auto_delete: This property marks the NVMe namespace for auto deletion when the volume containing the namespace runs out of space. This is most commonly set on namespace clones.<br/> When set to _true_, the NVMe namespace becomes eligible for automatic deletion when the volume runs out of space. Auto deletion only occurs when the volume containing the namespace is also configured for auto deletion and free space in the volume decreases below a particular threshold.<br/> This property is optional in POST and PATCH. The default value for a new NVMe namespace is _false_.<br/> There is an added cost to retrieving this property's value. It is not populated for either a collection GET or an instance GET unless it is explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more. 
                clone: 
                comment: A configurable comment available for use by the administrator. Valid in POST and PATCH. 
                create_time: The time the NVMe namespace was created.
                enabled: The enabled state of the NVMe namespace. Certain error conditions cause the namespace to become disabled. If the namespace is disabled, you can check the `state` property to determine what error disabled the namespace. An NVMe namespace is enabled automatically when it is created. 
                location: 
                metric: 
                name: The fully qualified path name of the NVMe namespace composed of a \"/vol\" prefix, the volume name, the (optional) qtree name and base name of the namespace. Valid in POST.<br/> NVMe namespaces do not support rename, or movement between volumes. 
                os_type: The operating system type of the NVMe namespace.<br/> Required in POST when creating an NVMe namespace that is not a clone of another. Disallowed in POST when creating a namespace clone. 
                space: 
                statistics: 
                status: 
                subsystem_map: 
                svm: 
                uuid: The unique identifier of the NVMe namespace. 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if auto_delete is not None:
                kwargs["auto_delete"] = auto_delete
            if clone is not None:
                kwargs["clone"] = clone
            if comment is not None:
                kwargs["comment"] = comment
            if create_time is not None:
                kwargs["create_time"] = create_time
            if enabled is not None:
                kwargs["enabled"] = enabled
            if location is not None:
                kwargs["location"] = location
            if metric is not None:
                kwargs["metric"] = metric
            if name is not None:
                kwargs["name"] = name
            if os_type is not None:
                kwargs["os_type"] = os_type
            if space is not None:
                kwargs["space"] = space
            if statistics is not None:
                kwargs["statistics"] = statistics
            if status is not None:
                kwargs["status"] = status
            if subsystem_map is not None:
                kwargs["subsystem_map"] = subsystem_map
            if svm is not None:
                kwargs["svm"] = svm
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = NvmeNamespace(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create NvmeNamespace: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an NVMe namespace.
### Related ONTAP commands
* `volume file clone autodelete`
* `vserver nvme namespace modify`
### Learn more
* [`DOC /storage/namespaces`](#docs-NVMe-storage_namespaces)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme namespace modify")
        async def nvme_namespace_modify(
        ) -> ResourceTable:
            """Modify an instance of a NvmeNamespace resource

            Args:
                auto_delete: This property marks the NVMe namespace for auto deletion when the volume containing the namespace runs out of space. This is most commonly set on namespace clones.<br/> When set to _true_, the NVMe namespace becomes eligible for automatic deletion when the volume runs out of space. Auto deletion only occurs when the volume containing the namespace is also configured for auto deletion and free space in the volume decreases below a particular threshold.<br/> This property is optional in POST and PATCH. The default value for a new NVMe namespace is _false_.<br/> There is an added cost to retrieving this property's value. It is not populated for either a collection GET or an instance GET unless it is explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more. 
                query_auto_delete: This property marks the NVMe namespace for auto deletion when the volume containing the namespace runs out of space. This is most commonly set on namespace clones.<br/> When set to _true_, the NVMe namespace becomes eligible for automatic deletion when the volume runs out of space. Auto deletion only occurs when the volume containing the namespace is also configured for auto deletion and free space in the volume decreases below a particular threshold.<br/> This property is optional in POST and PATCH. The default value for a new NVMe namespace is _false_.<br/> There is an added cost to retrieving this property's value. It is not populated for either a collection GET or an instance GET unless it is explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more. 
                comment: A configurable comment available for use by the administrator. Valid in POST and PATCH. 
                query_comment: A configurable comment available for use by the administrator. Valid in POST and PATCH. 
                create_time: The time the NVMe namespace was created.
                query_create_time: The time the NVMe namespace was created.
                enabled: The enabled state of the NVMe namespace. Certain error conditions cause the namespace to become disabled. If the namespace is disabled, you can check the `state` property to determine what error disabled the namespace. An NVMe namespace is enabled automatically when it is created. 
                query_enabled: The enabled state of the NVMe namespace. Certain error conditions cause the namespace to become disabled. If the namespace is disabled, you can check the `state` property to determine what error disabled the namespace. An NVMe namespace is enabled automatically when it is created. 
                name: The fully qualified path name of the NVMe namespace composed of a \"/vol\" prefix, the volume name, the (optional) qtree name and base name of the namespace. Valid in POST.<br/> NVMe namespaces do not support rename, or movement between volumes. 
                query_name: The fully qualified path name of the NVMe namespace composed of a \"/vol\" prefix, the volume name, the (optional) qtree name and base name of the namespace. Valid in POST.<br/> NVMe namespaces do not support rename, or movement between volumes. 
                os_type: The operating system type of the NVMe namespace.<br/> Required in POST when creating an NVMe namespace that is not a clone of another. Disallowed in POST when creating a namespace clone. 
                query_os_type: The operating system type of the NVMe namespace.<br/> Required in POST when creating an NVMe namespace that is not a clone of another. Disallowed in POST when creating a namespace clone. 
                uuid: The unique identifier of the NVMe namespace. 
                query_uuid: The unique identifier of the NVMe namespace. 
            """

            kwargs = {}
            changes = {}
            if query_auto_delete is not None:
                kwargs["auto_delete"] = query_auto_delete
            if query_comment is not None:
                kwargs["comment"] = query_comment
            if query_create_time is not None:
                kwargs["create_time"] = query_create_time
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_name is not None:
                kwargs["name"] = query_name
            if query_os_type is not None:
                kwargs["os_type"] = query_os_type
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if auto_delete is not None:
                changes["auto_delete"] = auto_delete
            if comment is not None:
                changes["comment"] = comment
            if create_time is not None:
                changes["create_time"] = create_time
            if enabled is not None:
                changes["enabled"] = enabled
            if name is not None:
                changes["name"] = name
            if os_type is not None:
                changes["os_type"] = os_type
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(NvmeNamespace, "find"):
                resource = NvmeNamespace.find(
                    **kwargs
                )
            else:
                resource = NvmeNamespace()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify NvmeNamespace: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an NVMe namespace.
### Related ONTAP commands
* `vserver nvme namespace delete`
### Learn more
* [`DOC /storage/namespaces`](#docs-NVMe-storage_namespaces)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme namespace delete")
        async def nvme_namespace_delete(
        ) -> None:
            """Delete an instance of a NvmeNamespace resource

            Args:
                auto_delete: This property marks the NVMe namespace for auto deletion when the volume containing the namespace runs out of space. This is most commonly set on namespace clones.<br/> When set to _true_, the NVMe namespace becomes eligible for automatic deletion when the volume runs out of space. Auto deletion only occurs when the volume containing the namespace is also configured for auto deletion and free space in the volume decreases below a particular threshold.<br/> This property is optional in POST and PATCH. The default value for a new NVMe namespace is _false_.<br/> There is an added cost to retrieving this property's value. It is not populated for either a collection GET or an instance GET unless it is explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more. 
                comment: A configurable comment available for use by the administrator. Valid in POST and PATCH. 
                create_time: The time the NVMe namespace was created.
                enabled: The enabled state of the NVMe namespace. Certain error conditions cause the namespace to become disabled. If the namespace is disabled, you can check the `state` property to determine what error disabled the namespace. An NVMe namespace is enabled automatically when it is created. 
                name: The fully qualified path name of the NVMe namespace composed of a \"/vol\" prefix, the volume name, the (optional) qtree name and base name of the namespace. Valid in POST.<br/> NVMe namespaces do not support rename, or movement between volumes. 
                os_type: The operating system type of the NVMe namespace.<br/> Required in POST when creating an NVMe namespace that is not a clone of another. Disallowed in POST when creating a namespace clone. 
                uuid: The unique identifier of the NVMe namespace. 
            """

            kwargs = {}
            if auto_delete is not None:
                kwargs["auto_delete"] = auto_delete
            if comment is not None:
                kwargs["comment"] = comment
            if create_time is not None:
                kwargs["create_time"] = create_time
            if enabled is not None:
                kwargs["enabled"] = enabled
            if name is not None:
                kwargs["name"] = name
            if os_type is not None:
                kwargs["os_type"] = os_type
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(NvmeNamespace, "find"):
                resource = NvmeNamespace.find(
                    **kwargs
                )
            else:
                resource = NvmeNamespace()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete NvmeNamespace: %s" % err)


