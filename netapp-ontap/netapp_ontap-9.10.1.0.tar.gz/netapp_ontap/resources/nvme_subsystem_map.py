r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
An NVMe subsystem map is an association of an NVMe namespace with an NVMe subsystem. When an NVMe namespace is mapped to an NVMe subsystem, the NVMe subsystem's hosts are granted access to the NVMe namespace. The relationship between an NVMe subsystem and an NVMe namespace is one subsystem to many namespaces.<br/>
The NVMe subsystem map REST API allows you to create, delete and discover NVMe subsystem maps.
## Examples
### Creating an NVMe subsystem map
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystemMap

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystemMap()
    resource.svm = {"name": "svm1"}
    resource.subsystem = {"name": "subsystem1"}
    resource.namespace = {"name": "/vol/vol1/namespace1"}
    resource.post(hydrate=True)
    print(resource)

```

---
### Retrieving all of the NVMe subsystem maps
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystemMap

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(NvmeSubsystemMap.get_collection()))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    NvmeSubsystemMap(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/0e91b214-fe40-11e8-91a0-005056a79967"
                    }
                },
                "uuid": "0e91b214-fe40-11e8-91a0-005056a79967",
                "name": "svm1",
            },
            "subsystem": {
                "uuid": "580a6b1e-fe43-11e8-91a0-005056a79967",
                "name": "subsystem1",
                "_links": {
                    "self": {
                        "href": "/api/protocols/nvme/subsystems/580a6b1e-fe43-11e8-91a0-005056a79967"
                    }
                },
            },
            "namespace": {
                "name": "/vol/vol1/namespace1",
                "uuid": "3ccdedc6-2519-4206-bc1f-b0f4adab6f89",
                "_links": {
                    "self": {
                        "href": "/api/storage/namespaces/3ccdedc6-2519-4206-bc1f-b0f4adab6f89"
                    }
                },
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/nvme/subsystem-maps/580a6b1e-fe43-11e8-91a0-005056a79967/3ccdedc6-2519-4206-bc1f-b0f4adab6f89"
                }
            },
        }
    )
]

```
</div>
</div>

---
### Retrieving a specific NVMe subsystem map
The NVMe subsystem map is identified by the UUID of the NVMe subsystem followed by the UUID of the NVMe namespace.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystemMap

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystemMap(
        **{
            "namespace.uuid": "3ccdedc6-2519-4206-bc1f-b0f4adab6f89",
            "subsystem.uuid": "580a6b1e-fe43-11e8-91a0-005056a79967",
        }
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
NvmeSubsystemMap(
    {
        "nsid": "00000001h",
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/0e91b214-fe40-11e8-91a0-005056a79967"}
            },
            "uuid": "0e91b214-fe40-11e8-91a0-005056a79967",
            "name": "svm1",
        },
        "subsystem": {
            "uuid": "580a6b1e-fe43-11e8-91a0-005056a79967",
            "name": "subsystem1",
            "_links": {
                "self": {
                    "href": "/api/protocols/nvme/subsystems/580a6b1e-fe43-11e8-91a0-005056a79967"
                }
            },
        },
        "namespace": {
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/012b4508-67d6-4788-8c2d-801f254ce976"
                    }
                },
                "uuid": "012b4508-67d6-4788-8c2d-801f254ce976",
                "name": "node1",
            },
            "name": "/vol/vol1/namespace1",
            "uuid": "3ccdedc6-2519-4206-bc1f-b0f4adab6f89",
            "_links": {
                "self": {
                    "href": "/api/storage/namespaces/3ccdedc6-2519-4206-bc1f-b0f4adab6f89"
                }
            },
        },
        "_links": {
            "self": {
                "href": "/api/protocols/nvme/subsystem-maps/580a6b1e-fe43-11e8-91a0-005056a79967/3ccdedc6-2519-4206-bc1f-b0f4adab6f89"
            }
        },
    }
)

```
</div>
</div>

---
### Deleting an NVMe subsystem map
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystemMap

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystemMap(
        **{
            "namespace.uuid": "3ccdedc6-2519-4206-bc1f-b0f4adab6f89",
            "subsystem.uuid": "580a6b1e-fe43-11e8-91a0-005056a79967",
        }
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


__all__ = ["NvmeSubsystemMap", "NvmeSubsystemMapSchema"]
__pdoc__ = {
    "NvmeSubsystemMapSchema.resource": False,
    "NvmeSubsystemMap.nvme_subsystem_map_show": False,
    "NvmeSubsystemMap.nvme_subsystem_map_create": False,
    "NvmeSubsystemMap.nvme_subsystem_map_modify": False,
    "NvmeSubsystemMap.nvme_subsystem_map_delete": False,
}


class NvmeSubsystemMapSchema(ResourceSchema):
    """The fields of the NvmeSubsystemMap object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the nvme_subsystem_map. """

    anagrpid = fields.Str(
        data_key="anagrpid",
    )
    r""" The Asymmetric Namespace Access Group ID (ANAGRPID) of the NVMe namespace.<br/>
The format for an ANAGRPID is 8 hexadecimal digits (zero-filled) followed by a lower case "h".<br/>
There is an added cost to retrieving this property's value. It is not populated for either a collection GET or an instance GET unless it is explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.


Example: 00103050h """

    namespace = fields.Nested("netapp_ontap.models.nvme_subsystem_map_namespace.NvmeSubsystemMapNamespaceSchema", data_key="namespace", unknown=EXCLUDE)
    r""" The namespace field of the nvme_subsystem_map. """

    nsid = fields.Str(
        data_key="nsid",
    )
    r""" The NVMe namespace identifier. This is an identifier used by an NVMe controller to provide access to the NVMe namespace.<br/>
The format for an NVMe namespace identifier is 8 hexadecimal digits (zero-filled) followed by a lower case "h".


Example: 00000001h """

    subsystem = fields.Nested("netapp_ontap.resources.nvme_subsystem.NvmeSubsystemSchema", data_key="subsystem", unknown=EXCLUDE)
    r""" The subsystem field of the nvme_subsystem_map. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the nvme_subsystem_map. """

    @property
    def resource(self):
        return NvmeSubsystemMap

    gettable_fields = [
        "links",
        "anagrpid",
        "namespace",
        "nsid",
        "subsystem.links",
        "subsystem.name",
        "subsystem.uuid",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,anagrpid,namespace,nsid,subsystem.links,subsystem.name,subsystem.uuid,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "svm.name",
        "svm.uuid",
    ]
    """svm.name,svm.uuid,"""

    postable_fields = [
        "namespace",
        "subsystem.name",
        "subsystem.uuid",
        "svm.name",
        "svm.uuid",
    ]
    """namespace,subsystem.name,subsystem.uuid,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NvmeSubsystemMap.get_collection(fields=field)]
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
            raise NetAppRestError("NvmeSubsystemMap modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NvmeSubsystemMap(Resource):
    r""" An NVMe subsystem map is an association of an NVMe namespace with an NVMe subsystem. When an NVMe namespace is mapped to an NVMe subsystem, the NVMe subsystem's hosts are granted access to the NVMe namespace. The relationship between an NVMe subsystem and an NVMe namespace is one subsystem to many namespaces. """

    _schema = NvmeSubsystemMapSchema
    _path = "/api/protocols/nvme/subsystem-maps"
    _keys = ["subsystem.uuid", "namespace.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves NVMe subsystem maps.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `anagrpid`
### Related ONTAP commands
* `vserver nvme subsystem map show`
### Learn more
* [`DOC /protocols/nvme/subsystem-maps`](#docs-NVMe-protocols_nvme_subsystem-maps)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme subsystem map show")
        def nvme_subsystem_map_show(
            fields: List[Choices.define(["anagrpid", "nsid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of NvmeSubsystemMap resources

            Args:
                anagrpid: The Asymmetric Namespace Access Group ID (ANAGRPID) of the NVMe namespace.<br/> The format for an ANAGRPID is 8 hexadecimal digits (zero-filled) followed by a lower case \"h\".<br/> There is an added cost to retrieving this property's value. It is not populated for either a collection GET or an instance GET unless it is explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more. 
                nsid: The NVMe namespace identifier. This is an identifier used by an NVMe controller to provide access to the NVMe namespace.<br/> The format for an NVMe namespace identifier is 8 hexadecimal digits (zero-filled) followed by a lower case \"h\". 
            """

            kwargs = {}
            if anagrpid is not None:
                kwargs["anagrpid"] = anagrpid
            if nsid is not None:
                kwargs["nsid"] = nsid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return NvmeSubsystemMap.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NvmeSubsystemMap resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["NvmeSubsystemMap"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["NvmeSubsystemMap"], NetAppResponse]:
        r"""Creates an NVMe subsystem map.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the NVMe subsystem map.
* `namespace.uuid` or `namespace.name` - Existing NVMe namespace to map to the specified NVme subsystem.
* `subsystem.uuid` or `subsystem.name` - Existing NVMe subsystem to map to the specified NVMe namespace.
### Related ONTAP commands
* `vserver nvme subsystem map create`
### Learn more
* [`DOC /protocols/nvme/subsystem-maps`](#docs-NVMe-protocols_nvme_subsystem-maps)
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
        records: Iterable["NvmeSubsystemMap"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an NVMe subsystem map.
### Related ONTAP commands
* `vserver nvme subsystem map delete`
### Learn more
* [`DOC /protocols/nvme/subsystem-maps`](#docs-NVMe-protocols_nvme_subsystem-maps)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves NVMe subsystem maps.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `anagrpid`
### Related ONTAP commands
* `vserver nvme subsystem map show`
### Learn more
* [`DOC /protocols/nvme/subsystem-maps`](#docs-NVMe-protocols_nvme_subsystem-maps)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an NVMe subsystem map.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `anagrpid`
### Related ONTAP commands
* `vserver nvme subsystem map show`
### Learn more
* [`DOC /protocols/nvme/subsystem-maps`](#docs-NVMe-protocols_nvme_subsystem-maps)
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
        r"""Creates an NVMe subsystem map.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the NVMe subsystem map.
* `namespace.uuid` or `namespace.name` - Existing NVMe namespace to map to the specified NVme subsystem.
* `subsystem.uuid` or `subsystem.name` - Existing NVMe subsystem to map to the specified NVMe namespace.
### Related ONTAP commands
* `vserver nvme subsystem map create`
### Learn more
* [`DOC /protocols/nvme/subsystem-maps`](#docs-NVMe-protocols_nvme_subsystem-maps)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme subsystem map create")
        async def nvme_subsystem_map_create(
        ) -> ResourceTable:
            """Create an instance of a NvmeSubsystemMap resource

            Args:
                links: 
                anagrpid: The Asymmetric Namespace Access Group ID (ANAGRPID) of the NVMe namespace.<br/> The format for an ANAGRPID is 8 hexadecimal digits (zero-filled) followed by a lower case \"h\".<br/> There is an added cost to retrieving this property's value. It is not populated for either a collection GET or an instance GET unless it is explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more. 
                namespace: 
                nsid: The NVMe namespace identifier. This is an identifier used by an NVMe controller to provide access to the NVMe namespace.<br/> The format for an NVMe namespace identifier is 8 hexadecimal digits (zero-filled) followed by a lower case \"h\". 
                subsystem: 
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if anagrpid is not None:
                kwargs["anagrpid"] = anagrpid
            if namespace is not None:
                kwargs["namespace"] = namespace
            if nsid is not None:
                kwargs["nsid"] = nsid
            if subsystem is not None:
                kwargs["subsystem"] = subsystem
            if svm is not None:
                kwargs["svm"] = svm

            resource = NvmeSubsystemMap(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create NvmeSubsystemMap: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an NVMe subsystem map.
### Related ONTAP commands
* `vserver nvme subsystem map delete`
### Learn more
* [`DOC /protocols/nvme/subsystem-maps`](#docs-NVMe-protocols_nvme_subsystem-maps)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme subsystem map delete")
        async def nvme_subsystem_map_delete(
        ) -> None:
            """Delete an instance of a NvmeSubsystemMap resource

            Args:
                anagrpid: The Asymmetric Namespace Access Group ID (ANAGRPID) of the NVMe namespace.<br/> The format for an ANAGRPID is 8 hexadecimal digits (zero-filled) followed by a lower case \"h\".<br/> There is an added cost to retrieving this property's value. It is not populated for either a collection GET or an instance GET unless it is explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more. 
                nsid: The NVMe namespace identifier. This is an identifier used by an NVMe controller to provide access to the NVMe namespace.<br/> The format for an NVMe namespace identifier is 8 hexadecimal digits (zero-filled) followed by a lower case \"h\". 
            """

            kwargs = {}
            if anagrpid is not None:
                kwargs["anagrpid"] = anagrpid
            if nsid is not None:
                kwargs["nsid"] = nsid

            if hasattr(NvmeSubsystemMap, "find"):
                resource = NvmeSubsystemMap.find(
                    **kwargs
                )
            else:
                resource = NvmeSubsystemMap()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete NvmeSubsystemMap: %s" % err)


