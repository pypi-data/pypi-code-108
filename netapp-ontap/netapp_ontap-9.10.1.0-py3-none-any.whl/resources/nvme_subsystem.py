r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
An NVMe subsystem maintains configuration state and namespace access control for a set of NVMe-connected hosts.<br/>
The NVMe subsystem REST API allows you to create, update, delete, and discover NVMe subsystems as well as add and remove NVMe hosts that can access the subsystem and associated namespaces.
## Examples
### Creating an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem()
    resource.svm = {"name": "svm1"}
    resource.name = "subsystem1"
    resource.os_type = "linux"
    resource.post(hydrate=True)
    print(resource)

```

---
### Creating an NVMe subsystem with multiple NVMe subsystem hosts
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem()
    resource.svm = {"name": "svm1"}
    resource.name = "subsystem2"
    resource.os_type = "vmware"
    resource.hosts = [
        {"nqn": "nqn.1992-01.example.com:host1"},
        {"nqn": "nqn.1992-01.example.com:host2"},
    ]
    resource.post(hydrate=True)
    print(resource)

```

---
### Retrieving all NVMe subsystems
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(NvmeSubsystem.get_collection()))

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    NvmeSubsystem(
        {
            "svm": {"uuid": "a009a9e7-4081-b576-7575-ada21efcaf16", "name": "svm1"},
            "uuid": "acde901a-a379-4a91-9ea6-1b728ed6696f",
            "name": "subsystem1",
        }
    ),
    NvmeSubsystem(
        {
            "svm": {"uuid": "a009a9e7-4081-b576-7575-ada21efcaf16", "name": "svm1"},
            "uuid": "bcde901a-a379-4a91-9ea6-1b728ed6696f",
            "name": "subsystem2",
        }
    ),
]

```
</div>
</div>

---
### Retrieving all NVMe subsystems with OS type _linux_
Note that the `os_type` query parameter is used to perform the query.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(NvmeSubsystem.get_collection(os_type="linux")))

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
[
    NvmeSubsystem(
        {
            "os_type": "linux",
            "svm": {"uuid": "a009a9e7-4081-b576-7575-ada21efcaf16", "name": "svm1"},
            "uuid": "acde901a-a379-4a91-9ea6-1b728ed6696f",
            "name": "subsystem1",
        }
    )
]

```
</div>
</div>

---
### Retrieving a specific NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem(uuid="acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
NvmeSubsystem(
    {
        "io_queue": {"default": {"count": 4, "depth": 32}},
        "os_type": "linux",
        "target_nqn": "nqn.1992-08.com.netapp:sn.d04594ef915b4c73b642169e72e4c0b1:subsystem.subsystem1",
        "svm": {"uuid": "a009a9e7-4081-b576-7575-ada21efcaf16", "name": "svm1"},
        "uuid": "acde901a-a379-4a91-9ea6-1b728ed6696f",
        "name": "subsystem1",
        "serial_number": "wtJNKNKD-uPLAAAAAAAD",
    }
)

```
</div>
</div>

---
### Retrieving the NVMe namespaces mapped to a specific NVMe subsystem
Note that the `fields` query parameter is used to specify the desired properties.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem(uuid="acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.get(fields="subsystem_maps")
    print(resource)

```
<div class="try_it_out">
<input id="example5_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example5_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example5_result" class="try_it_out_content">
```
NvmeSubsystem(
    {
        "svm": {"uuid": "a009a9e7-4081-b576-7575-ada21efcaf16", "name": "svm1"},
        "uuid": "acde901a-a379-4a91-9ea6-1b728ed6696f",
        "subsystem_maps": [
            {
                "anagrpid": "00000001h",
                "namespace": {
                    "name": "/vol/vol1/namespace1",
                    "uuid": "eeaaca23-128d-4a7d-be4a-dc9106705799",
                },
                "nsid": "00000001h",
            },
            {
                "anagrpid": "00000002h",
                "namespace": {
                    "name": "/vol/vol1/namespace2",
                    "uuid": "feaaca23-83a0-4a7d-beda-dc9106705799",
                },
                "nsid": "00000002h",
            },
        ],
        "name": "subsystem1",
    }
)

```
</div>
</div>

---
### Adding a comment about an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem(uuid="acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.comment = "A brief comment about the subsystem"
    resource.patch()

```

---
### Deleting an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem(uuid="acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.delete()

```

### Deleting an NVMe subsystem with mapped NVMe namespaces
Normally, deleting an NVMe subsystem that has mapped NVMe namespaces is not allowed. The deletion can be forced using the `allow_delete_while_mapped` query parameter.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem(uuid="acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.delete(allow_delete_while_mapped=True)

```

### Delete an NVMe subsystem with NVMe subsystem hosts
Normally, deleting an NVMe subsystem with NVMe subsystem hosts is disallowed. The deletion can be forced using the `allow_delete_with_hosts` query parameter.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem(uuid="acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.delete(allow_delete_with_hosts=True)

```

---
## An NVMe Subsystem Host
An NVMe subsystem host is a network host provisioned to an NVMe subsystem to access namespaces mapped to that subsystem.
## Examples
### Adding an NVMe subsystem host to an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystemHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystemHost("acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.nqn = "nqn.1992-01.com.example:subsys1.host1"
    resource.post(hydrate=True)
    print(resource)

```

---
### Adding multiple NVMe subsystem hosts to an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystemHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystemHost("acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.records = [
        {"nqn": "nqn.1992-01.com.example:subsys1.host2"},
        {"nqn": "nqn.1992-01.com.example:subsys1.host3"},
    ]
    resource.post(hydrate=True)
    print(resource)

```

---
### Retrieving all NVMe subsystem hosts for an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystemHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(NvmeSubsystemHost.get_collection("acde901a-a379-4a91-9ea6-1b728ed6696f"))
    )

```
<div class="try_it_out">
<input id="example12_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example12_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example12_result" class="try_it_out_content">
```
[
    NvmeSubsystemHost({"nqn": "nqn.1992-01.com.example:subsys1.host1"}),
    NvmeSubsystemHost({"nqn": "nqn.1992-01.com.example:subsys1.host2"}),
    NvmeSubsystemHost({"nqn": "nqn.1992-01.com.example:subsys1.host3"}),
]

```
</div>
</div>

---
### Retrieving a specific NVMe subsystem host for an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystemHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystemHost(
        "acde901a-a379-4a91-9ea6-1b728ed6696f",
        nqn="nqn.1992-01.com.example:subsys1.host1",
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example13_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example13_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example13_result" class="try_it_out_content">
```
NvmeSubsystemHost(
    {
        "io_queue": {"count": 4, "depth": 32},
        "nqn": "nqn.1992-01.com.example:subsys1.host1",
        "subsystem": {"uuid": "acde901a-a379-4a91-9ea6-1b728ed6696f"},
    }
)

```
</div>
</div>

---
### Deleting an NVMe subsystem host from an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystemHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystemHost(
        "acde901a-a379-4a91-9ea6-1b728ed6696f",
        nqn="nqn.1992-01.com.example:subsys1.host1",
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


__all__ = ["NvmeSubsystem", "NvmeSubsystemSchema"]
__pdoc__ = {
    "NvmeSubsystemSchema.resource": False,
    "NvmeSubsystem.nvme_subsystem_show": False,
    "NvmeSubsystem.nvme_subsystem_create": False,
    "NvmeSubsystem.nvme_subsystem_modify": False,
    "NvmeSubsystem.nvme_subsystem_delete": False,
}


class NvmeSubsystemSchema(ResourceSchema):
    """The fields of the NvmeSubsystem object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the nvme_subsystem. """

    comment = fields.Str(
        data_key="comment",
        validate=len_validation(minimum=0, maximum=255),
    )
    r""" A configurable comment for the NVMe subsystem. Optional in POST and PATCH. """

    delete_on_unmap = fields.Boolean(
        data_key="delete_on_unmap",
    )
    r""" An option that causes the subsystem to be deleted when the last subsystem map associated with it is deleted. This property defaults to _false_ when the subsystem is created. """

    hosts = fields.List(fields.Nested("netapp_ontap.models.nvme_subsystem_hosts.NvmeSubsystemHostsSchema", unknown=EXCLUDE), data_key="hosts")
    r""" The NVMe hosts configured for access to the NVMe subsystem. Optional in POST. """

    io_queue = fields.Nested("netapp_ontap.models.nvme_subsystem_io_queue.NvmeSubsystemIoQueueSchema", data_key="io_queue", unknown=EXCLUDE)
    r""" The io_queue field of the nvme_subsystem. """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=1, maximum=96),
    )
    r""" The name of the NVMe subsystem. Once created, an NVMe subsystem cannot be renamed. Required in POST.


Example: subsystem1 """

    os_type = fields.Str(
        data_key="os_type",
        validate=enum_validation(['aix', 'linux', 'vmware', 'windows']),
    )
    r""" The host operating system of the NVMe subsystem's hosts. Required in POST.


Valid choices:

* aix
* linux
* vmware
* windows """

    serial_number = fields.Str(
        data_key="serial_number",
        validate=len_validation(minimum=20, maximum=20),
    )
    r""" The serial number of the NVMe subsystem.


Example: wCVsgFMiuMhVAAAAAAAB """

    subsystem_maps = fields.List(fields.Nested("netapp_ontap.models.nvme_subsystem_subsystem_maps.NvmeSubsystemSubsystemMapsSchema", unknown=EXCLUDE), data_key="subsystem_maps")
    r""" The NVMe namespaces mapped to the NVMe subsystem.<br/>
There is an added cost to retrieving property values for `subsystem_maps`. They are not populated for either a collection GET or an instance GET unless explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the nvme_subsystem. """

    target_nqn = fields.Str(
        data_key="target_nqn",
        validate=len_validation(minimum=1, maximum=223),
    )
    r""" The NVMe qualified name (NQN) used to identify the NVMe storage target.


Example: nqn.1992-01.example.com:string """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The unique identifier of the NVMe subsystem.


Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    vendor_uuids = fields.List(fields.Str, data_key="vendor_uuids")
    r""" Vendor-specific identifiers (UUIDs) optionally assigned to an NVMe subsystem when the subsystem is created. The identifiers are used to enable vendor-specific NVMe protocol features. The identifiers are provided by a host application vendor and shared with NetApp prior to a joint product release. Creating an NVMe subsystem with an unknown or non-specific identifier will have no effect on the NVMe subsystem. Refer to the ONTAP SAN Administration Guide for a list of the supported vendor-specific identifiers. After a subsystem is created, the vendor-specific identifiers cannot be changed or removed. Optional in POST. """

    @property
    def resource(self):
        return NvmeSubsystem

    gettable_fields = [
        "links",
        "comment",
        "delete_on_unmap",
        "hosts",
        "io_queue",
        "name",
        "os_type",
        "serial_number",
        "subsystem_maps",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "target_nqn",
        "uuid",
        "vendor_uuids",
    ]
    """links,comment,delete_on_unmap,hosts,io_queue,name,os_type,serial_number,subsystem_maps,svm.links,svm.name,svm.uuid,target_nqn,uuid,vendor_uuids,"""

    patchable_fields = [
        "comment",
        "delete_on_unmap",
        "io_queue",
        "svm.name",
        "svm.uuid",
    ]
    """comment,delete_on_unmap,io_queue,svm.name,svm.uuid,"""

    postable_fields = [
        "comment",
        "delete_on_unmap",
        "hosts",
        "io_queue",
        "name",
        "os_type",
        "svm.name",
        "svm.uuid",
        "vendor_uuids",
    ]
    """comment,delete_on_unmap,hosts,io_queue,name,os_type,svm.name,svm.uuid,vendor_uuids,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NvmeSubsystem.get_collection(fields=field)]
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
            raise NetAppRestError("NvmeSubsystem modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NvmeSubsystem(Resource):
    r""" An NVMe subsystem maintains configuration state and namespace access control for a set of NVMe-connected hosts. """

    _schema = NvmeSubsystemSchema
    _path = "/api/protocols/nvme/subsystems"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves NVMe subsystems.
### Related ONTAP commands
* `vserver nvme subsystem host show`
* `vserver nvme subsystem map show`
* `vserver nvme subsystem show`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme subsystem show")
        def nvme_subsystem_show(
            fields: List[Choices.define(["comment", "delete_on_unmap", "name", "os_type", "serial_number", "target_nqn", "uuid", "vendor_uuids", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of NvmeSubsystem resources

            Args:
                comment: A configurable comment for the NVMe subsystem. Optional in POST and PATCH. 
                delete_on_unmap: An option that causes the subsystem to be deleted when the last subsystem map associated with it is deleted. This property defaults to _false_ when the subsystem is created. 
                name: The name of the NVMe subsystem. Once created, an NVMe subsystem cannot be renamed. Required in POST. 
                os_type: The host operating system of the NVMe subsystem's hosts. Required in POST. 
                serial_number: The serial number of the NVMe subsystem. 
                target_nqn: The NVMe qualified name (NQN) used to identify the NVMe storage target. 
                uuid: The unique identifier of the NVMe subsystem. 
                vendor_uuids: Vendor-specific identifiers (UUIDs) optionally assigned to an NVMe subsystem when the subsystem is created. The identifiers are used to enable vendor-specific NVMe protocol features. The identifiers are provided by a host application vendor and shared with NetApp prior to a joint product release. Creating an NVMe subsystem with an unknown or non-specific identifier will have no effect on the NVMe subsystem. Refer to the ONTAP SAN Administration Guide for a list of the supported vendor-specific identifiers. After a subsystem is created, the vendor-specific identifiers cannot be changed or removed. Optional in POST. 
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if delete_on_unmap is not None:
                kwargs["delete_on_unmap"] = delete_on_unmap
            if name is not None:
                kwargs["name"] = name
            if os_type is not None:
                kwargs["os_type"] = os_type
            if serial_number is not None:
                kwargs["serial_number"] = serial_number
            if target_nqn is not None:
                kwargs["target_nqn"] = target_nqn
            if uuid is not None:
                kwargs["uuid"] = uuid
            if vendor_uuids is not None:
                kwargs["vendor_uuids"] = vendor_uuids
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return NvmeSubsystem.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NvmeSubsystem resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["NvmeSubsystem"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an NVMe subsystem.
### Related ONTAP commands
* `vserver nvme subsystem modify`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["NvmeSubsystem"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["NvmeSubsystem"], NetAppResponse]:
        r"""Creates an NVMe subsystem.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the NVMe subsystem.
* `name` - Name for NVMe subsystem. Once created, an NVMe subsytem cannot be renamed.
* `os_type` - Operating system of the NVMe subsystem's hosts.
### Related ONTAP commands
* `vserver nvme subsystem create`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
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
        records: Iterable["NvmeSubsystem"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Removes an NVMe subsystem.
### Related ONTAP commands
* `vserver nvme subsystem delete`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves NVMe subsystems.
### Related ONTAP commands
* `vserver nvme subsystem host show`
* `vserver nvme subsystem map show`
* `vserver nvme subsystem show`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an NVMe subsystem.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `subsystem_maps.*`
### Related ONTAP commands
* `vserver nvme subsystem host show`
* `vserver nvme subsystem map show`
* `vserver nvme subsystem show`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
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
        r"""Creates an NVMe subsystem.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the NVMe subsystem.
* `name` - Name for NVMe subsystem. Once created, an NVMe subsytem cannot be renamed.
* `os_type` - Operating system of the NVMe subsystem's hosts.
### Related ONTAP commands
* `vserver nvme subsystem create`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme subsystem create")
        async def nvme_subsystem_create(
        ) -> ResourceTable:
            """Create an instance of a NvmeSubsystem resource

            Args:
                links: 
                comment: A configurable comment for the NVMe subsystem. Optional in POST and PATCH. 
                delete_on_unmap: An option that causes the subsystem to be deleted when the last subsystem map associated with it is deleted. This property defaults to _false_ when the subsystem is created. 
                hosts: The NVMe hosts configured for access to the NVMe subsystem. Optional in POST. 
                io_queue: 
                name: The name of the NVMe subsystem. Once created, an NVMe subsystem cannot be renamed. Required in POST. 
                os_type: The host operating system of the NVMe subsystem's hosts. Required in POST. 
                serial_number: The serial number of the NVMe subsystem. 
                subsystem_maps: The NVMe namespaces mapped to the NVMe subsystem.<br/> There is an added cost to retrieving property values for `subsystem_maps`. They are not populated for either a collection GET or an instance GET unless explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more. 
                svm: 
                target_nqn: The NVMe qualified name (NQN) used to identify the NVMe storage target. 
                uuid: The unique identifier of the NVMe subsystem. 
                vendor_uuids: Vendor-specific identifiers (UUIDs) optionally assigned to an NVMe subsystem when the subsystem is created. The identifiers are used to enable vendor-specific NVMe protocol features. The identifiers are provided by a host application vendor and shared with NetApp prior to a joint product release. Creating an NVMe subsystem with an unknown or non-specific identifier will have no effect on the NVMe subsystem. Refer to the ONTAP SAN Administration Guide for a list of the supported vendor-specific identifiers. After a subsystem is created, the vendor-specific identifiers cannot be changed or removed. Optional in POST. 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if comment is not None:
                kwargs["comment"] = comment
            if delete_on_unmap is not None:
                kwargs["delete_on_unmap"] = delete_on_unmap
            if hosts is not None:
                kwargs["hosts"] = hosts
            if io_queue is not None:
                kwargs["io_queue"] = io_queue
            if name is not None:
                kwargs["name"] = name
            if os_type is not None:
                kwargs["os_type"] = os_type
            if serial_number is not None:
                kwargs["serial_number"] = serial_number
            if subsystem_maps is not None:
                kwargs["subsystem_maps"] = subsystem_maps
            if svm is not None:
                kwargs["svm"] = svm
            if target_nqn is not None:
                kwargs["target_nqn"] = target_nqn
            if uuid is not None:
                kwargs["uuid"] = uuid
            if vendor_uuids is not None:
                kwargs["vendor_uuids"] = vendor_uuids

            resource = NvmeSubsystem(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create NvmeSubsystem: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an NVMe subsystem.
### Related ONTAP commands
* `vserver nvme subsystem modify`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme subsystem modify")
        async def nvme_subsystem_modify(
        ) -> ResourceTable:
            """Modify an instance of a NvmeSubsystem resource

            Args:
                comment: A configurable comment for the NVMe subsystem. Optional in POST and PATCH. 
                query_comment: A configurable comment for the NVMe subsystem. Optional in POST and PATCH. 
                delete_on_unmap: An option that causes the subsystem to be deleted when the last subsystem map associated with it is deleted. This property defaults to _false_ when the subsystem is created. 
                query_delete_on_unmap: An option that causes the subsystem to be deleted when the last subsystem map associated with it is deleted. This property defaults to _false_ when the subsystem is created. 
                name: The name of the NVMe subsystem. Once created, an NVMe subsystem cannot be renamed. Required in POST. 
                query_name: The name of the NVMe subsystem. Once created, an NVMe subsystem cannot be renamed. Required in POST. 
                os_type: The host operating system of the NVMe subsystem's hosts. Required in POST. 
                query_os_type: The host operating system of the NVMe subsystem's hosts. Required in POST. 
                serial_number: The serial number of the NVMe subsystem. 
                query_serial_number: The serial number of the NVMe subsystem. 
                target_nqn: The NVMe qualified name (NQN) used to identify the NVMe storage target. 
                query_target_nqn: The NVMe qualified name (NQN) used to identify the NVMe storage target. 
                uuid: The unique identifier of the NVMe subsystem. 
                query_uuid: The unique identifier of the NVMe subsystem. 
                vendor_uuids: Vendor-specific identifiers (UUIDs) optionally assigned to an NVMe subsystem when the subsystem is created. The identifiers are used to enable vendor-specific NVMe protocol features. The identifiers are provided by a host application vendor and shared with NetApp prior to a joint product release. Creating an NVMe subsystem with an unknown or non-specific identifier will have no effect on the NVMe subsystem. Refer to the ONTAP SAN Administration Guide for a list of the supported vendor-specific identifiers. After a subsystem is created, the vendor-specific identifiers cannot be changed or removed. Optional in POST. 
                query_vendor_uuids: Vendor-specific identifiers (UUIDs) optionally assigned to an NVMe subsystem when the subsystem is created. The identifiers are used to enable vendor-specific NVMe protocol features. The identifiers are provided by a host application vendor and shared with NetApp prior to a joint product release. Creating an NVMe subsystem with an unknown or non-specific identifier will have no effect on the NVMe subsystem. Refer to the ONTAP SAN Administration Guide for a list of the supported vendor-specific identifiers. After a subsystem is created, the vendor-specific identifiers cannot be changed or removed. Optional in POST. 
            """

            kwargs = {}
            changes = {}
            if query_comment is not None:
                kwargs["comment"] = query_comment
            if query_delete_on_unmap is not None:
                kwargs["delete_on_unmap"] = query_delete_on_unmap
            if query_name is not None:
                kwargs["name"] = query_name
            if query_os_type is not None:
                kwargs["os_type"] = query_os_type
            if query_serial_number is not None:
                kwargs["serial_number"] = query_serial_number
            if query_target_nqn is not None:
                kwargs["target_nqn"] = query_target_nqn
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid
            if query_vendor_uuids is not None:
                kwargs["vendor_uuids"] = query_vendor_uuids

            if comment is not None:
                changes["comment"] = comment
            if delete_on_unmap is not None:
                changes["delete_on_unmap"] = delete_on_unmap
            if name is not None:
                changes["name"] = name
            if os_type is not None:
                changes["os_type"] = os_type
            if serial_number is not None:
                changes["serial_number"] = serial_number
            if target_nqn is not None:
                changes["target_nqn"] = target_nqn
            if uuid is not None:
                changes["uuid"] = uuid
            if vendor_uuids is not None:
                changes["vendor_uuids"] = vendor_uuids

            if hasattr(NvmeSubsystem, "find"):
                resource = NvmeSubsystem.find(
                    **kwargs
                )
            else:
                resource = NvmeSubsystem()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify NvmeSubsystem: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Removes an NVMe subsystem.
### Related ONTAP commands
* `vserver nvme subsystem delete`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme subsystem delete")
        async def nvme_subsystem_delete(
        ) -> None:
            """Delete an instance of a NvmeSubsystem resource

            Args:
                comment: A configurable comment for the NVMe subsystem. Optional in POST and PATCH. 
                delete_on_unmap: An option that causes the subsystem to be deleted when the last subsystem map associated with it is deleted. This property defaults to _false_ when the subsystem is created. 
                name: The name of the NVMe subsystem. Once created, an NVMe subsystem cannot be renamed. Required in POST. 
                os_type: The host operating system of the NVMe subsystem's hosts. Required in POST. 
                serial_number: The serial number of the NVMe subsystem. 
                target_nqn: The NVMe qualified name (NQN) used to identify the NVMe storage target. 
                uuid: The unique identifier of the NVMe subsystem. 
                vendor_uuids: Vendor-specific identifiers (UUIDs) optionally assigned to an NVMe subsystem when the subsystem is created. The identifiers are used to enable vendor-specific NVMe protocol features. The identifiers are provided by a host application vendor and shared with NetApp prior to a joint product release. Creating an NVMe subsystem with an unknown or non-specific identifier will have no effect on the NVMe subsystem. Refer to the ONTAP SAN Administration Guide for a list of the supported vendor-specific identifiers. After a subsystem is created, the vendor-specific identifiers cannot be changed or removed. Optional in POST. 
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if delete_on_unmap is not None:
                kwargs["delete_on_unmap"] = delete_on_unmap
            if name is not None:
                kwargs["name"] = name
            if os_type is not None:
                kwargs["os_type"] = os_type
            if serial_number is not None:
                kwargs["serial_number"] = serial_number
            if target_nqn is not None:
                kwargs["target_nqn"] = target_nqn
            if uuid is not None:
                kwargs["uuid"] = uuid
            if vendor_uuids is not None:
                kwargs["vendor_uuids"] = vendor_uuids

            if hasattr(NvmeSubsystem, "find"):
                resource = NvmeSubsystem.find(
                    **kwargs
                )
            else:
                resource = NvmeSubsystem()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete NvmeSubsystem: %s" % err)


