r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
A Non-Volatile Memory Express (NVMe) service defines the properties of the NVMe controller target for an SVM. There can be at most one NVMe service for an SVM. An SVM's NVMe service must be created before NVMe host initiators can connect to the SVM.<br/>
The Non-Volatile Memory Express (NVMe) service REST API allows you to create, update, delete, and discover NVMe services for SVMs.
## Performance monitoring
Performance of the SVM can be monitored by the `metric.*` and `statistics.*` properties. These show the performance of the SVM in terms of IOPS, latency and throughput. The `metric.*` properties denote an average whereas `statistics.*` properties denote a real-time monotonically increasing value aggregated across all nodes.
## Examples
### Creating an NVMe service for an SVM
The simpliest way to create an NVMe service is to specify only the SVM, either by name or UUID. By default, the new NVMe service is enabled.<br/>
In this example, the `return_records` query parameter is used to retrieve the new NVMe service object in the REST response.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeService()
    resource.svm = {"name": "svm1"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
NvmeService(
    {
        "enabled": True,
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/bfb1beb0-dc69-11e8-b29f-005056bb7341"}
            },
            "uuid": "bfb1beb0-dc69-11e8-b29f-005056bb7341",
            "name": "svm1",
        },
        "_links": {
            "self": {
                "href": "/api/protocols/nvme/services/bfb1beb0-dc69-11e8-b29f-005056bb7341"
            }
        },
    }
)

```
</div>
</div>

---
### Retrieving the NVMe services for all SVMs in the cluster
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(NvmeService.get_collection()))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    NvmeService(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/ab60c350-dc68-11e8-9711-005056bbe408"
                    }
                },
                "uuid": "ab60c350-dc68-11e8-9711-005056bbe408",
                "name": "svm0",
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/nvme/services/ab60c350-dc68-11e8-9711-005056bbe408"
                }
            },
        }
    ),
    NvmeService(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/bfb1beb0-dc69-11e8-b29f-005056bb7341"
                    }
                },
                "uuid": "bfb1beb0-dc69-11e8-b29f-005056bb7341",
                "name": "svm1",
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/nvme/services/bfb1beb0-dc69-11e8-b29f-005056bb7341"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving details for a specific NVMe service
The NVMe service is identified by the UUID of its SVM.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeService(**{"svm.uuid": "bfb1beb0-dc69-11e8-b29f-005056bb7341"})
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
NvmeService(
    {
        "enabled": True,
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/bfb1beb0-dc69-11e8-b29f-005056bb7341"}
            },
            "uuid": "bfb1beb0-dc69-11e8-b29f-005056bb7341",
            "name": "svm1",
        },
        "_links": {
            "self": {
                "href": "/api/protocols/nvme/services/bfb1beb0-dc69-11e8-b29f-005056bb7341"
            }
        },
    }
)

```
</div>
</div>

---
### Disabling an NVMe service
Disabling an NVMe service shuts down all active NVMe connections for the SVM and prevents the creation of new NVMe connections.<br/>
The NVMe service to update is identified by the UUID of its SVM.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeService(**{"svm.uuid": "bfb1beb0-dc69-11e8-b29f-005056bb7341"})
    resource.enabled = False
    resource.patch()

```

<br/>
You can retrieve the NVMe service to confirm the change.<br/>
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeService(**{"svm.uuid": "bfb1beb0-dc69-11e8-b29f-005056bb7341"})
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
NvmeService(
    {
        "enabled": False,
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/bfb1beb0-dc69-11e8-b29f-005056bb7341"}
            },
            "uuid": "bfb1beb0-dc69-11e8-b29f-005056bb7341",
            "name": "svm1",
        },
        "_links": {
            "self": {
                "href": "/api/protocols/nvme/services/bfb1beb0-dc69-11e8-b29f-005056bb7341"
            }
        },
    }
)

```
</div>
</div>

---
### Deleting an NVMe service
The NVMe service must be disabled before it can be deleted. In addition, all NVMe interfaces, subsystems, and subsystem maps associated with the SVM must first be deleted.<br/>
The NVMe service to delete is identified by the UUID of its SVM.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeService(**{"svm.uuid": "bfb1beb0-dc69-11e8-b29f-005056bb7341"})
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


__all__ = ["NvmeService", "NvmeServiceSchema"]
__pdoc__ = {
    "NvmeServiceSchema.resource": False,
    "NvmeService.nvme_service_show": False,
    "NvmeService.nvme_service_create": False,
    "NvmeService.nvme_service_modify": False,
    "NvmeService.nvme_service_delete": False,
}


class NvmeServiceSchema(ResourceSchema):
    """The fields of the NvmeService object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the nvme_service. """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" The administrative state of the NVMe service. The NVMe service can be disabled to block all NVMe connectivity to the SVM.<br/>
This is optional in POST and PATCH. The default setting is _true_ (enabled) in POST. """

    metric = fields.Nested("netapp_ontap.models.nvme_service_metric.NvmeServiceMetricSchema", data_key="metric", unknown=EXCLUDE)
    r""" The metric field of the nvme_service. """

    statistics = fields.Nested("netapp_ontap.models.nvme_service_statistics.NvmeServiceStatisticsSchema", data_key="statistics", unknown=EXCLUDE)
    r""" The statistics field of the nvme_service. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the nvme_service. """

    @property
    def resource(self):
        return NvmeService

    gettable_fields = [
        "links",
        "enabled",
        "metric",
        "statistics",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,enabled,metric,statistics,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "enabled",
        "svm.name",
        "svm.uuid",
    ]
    """enabled,svm.name,svm.uuid,"""

    postable_fields = [
        "enabled",
        "svm.name",
        "svm.uuid",
    ]
    """enabled,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NvmeService.get_collection(fields=field)]
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
            raise NetAppRestError("NvmeService modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NvmeService(Resource):
    r""" A Non-Volatile Memory Express (NVMe) service defines the properties of the NVMe controller target for an SVM. There can be at most one NVMe service for an SVM. An SVM's NVMe service must be created before NVMe host initiators can connect to the SVM.<br/>
An NVMe service is identified by the UUID of its SVM. """

    _schema = NvmeServiceSchema
    _path = "/api/protocols/nvme/services"
    _keys = ["svm.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves NVMe services.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `vserver nvme show`
### Learn more
* [`DOC /protocols/nvme/services`](#docs-NVMe-protocols_nvme_services)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme service show")
        def nvme_service_show(
            fields: List[Choices.define(["enabled", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of NvmeService resources

            Args:
                enabled: The administrative state of the NVMe service. The NVMe service can be disabled to block all NVMe connectivity to the SVM.<br/> This is optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return NvmeService.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NvmeService resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["NvmeService"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an NVMe service.
### Related ONTAP commands
* `vserver nvme modify`
### Learn more
* [`DOC /protocols/nvme/services`](#docs-NVMe-protocols_nvme_services)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["NvmeService"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["NvmeService"], NetAppResponse]:
        r"""Creates an NVMe service.
### Required properties
* `svm.uuid` or `svm.name` - The existing SVM in which to create the NVMe service.
### Related ONTAP commands
* `vserver nvme create`
### Learn more
* [`DOC /protocols/nvme/services`](#docs-NVMe-protocols_nvme_services)
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
        records: Iterable["NvmeService"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an NVMe service. An NVMe service must be disabled before it can be deleted. In addition, all NVMe interfaces, subsystems, and subsystem maps associated with the SVM must first be deleted.
### Related ONTAP commands
* `vserver nvme delete`
### Learn more
* [`DOC /protocols/nvme/services`](#docs-NVMe-protocols_nvme_services)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves NVMe services.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `vserver nvme show`
### Learn more
* [`DOC /protocols/nvme/services`](#docs-NVMe-protocols_nvme_services)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an NVMe service.
### Related ONTAP commands
* `vserver nvme show`
### Learn more
* [`DOC /protocols/nvme/services`](#docs-NVMe-protocols_nvme_services)
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
        r"""Creates an NVMe service.
### Required properties
* `svm.uuid` or `svm.name` - The existing SVM in which to create the NVMe service.
### Related ONTAP commands
* `vserver nvme create`
### Learn more
* [`DOC /protocols/nvme/services`](#docs-NVMe-protocols_nvme_services)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme service create")
        async def nvme_service_create(
        ) -> ResourceTable:
            """Create an instance of a NvmeService resource

            Args:
                links: 
                enabled: The administrative state of the NVMe service. The NVMe service can be disabled to block all NVMe connectivity to the SVM.<br/> This is optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
                metric: 
                statistics: 
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if enabled is not None:
                kwargs["enabled"] = enabled
            if metric is not None:
                kwargs["metric"] = metric
            if statistics is not None:
                kwargs["statistics"] = statistics
            if svm is not None:
                kwargs["svm"] = svm

            resource = NvmeService(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create NvmeService: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an NVMe service.
### Related ONTAP commands
* `vserver nvme modify`
### Learn more
* [`DOC /protocols/nvme/services`](#docs-NVMe-protocols_nvme_services)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme service modify")
        async def nvme_service_modify(
        ) -> ResourceTable:
            """Modify an instance of a NvmeService resource

            Args:
                enabled: The administrative state of the NVMe service. The NVMe service can be disabled to block all NVMe connectivity to the SVM.<br/> This is optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
                query_enabled: The administrative state of the NVMe service. The NVMe service can be disabled to block all NVMe connectivity to the SVM.<br/> This is optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
            """

            kwargs = {}
            changes = {}
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled

            if enabled is not None:
                changes["enabled"] = enabled

            if hasattr(NvmeService, "find"):
                resource = NvmeService.find(
                    **kwargs
                )
            else:
                resource = NvmeService()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify NvmeService: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an NVMe service. An NVMe service must be disabled before it can be deleted. In addition, all NVMe interfaces, subsystems, and subsystem maps associated with the SVM must first be deleted.
### Related ONTAP commands
* `vserver nvme delete`
### Learn more
* [`DOC /protocols/nvme/services`](#docs-NVMe-protocols_nvme_services)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme service delete")
        async def nvme_service_delete(
        ) -> None:
            """Delete an instance of a NvmeService resource

            Args:
                enabled: The administrative state of the NVMe service. The NVMe service can be disabled to block all NVMe connectivity to the SVM.<br/> This is optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled

            if hasattr(NvmeService, "find"):
                resource = NvmeService.find(
                    **kwargs
                )
            else:
                resource = NvmeService()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete NvmeService: %s" % err)


