r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
A Fibre Channel Protocol (FC Protocol) service defines the properties of the FC Protocol target for an SVM. There can be at most one FC Protocol service for an SVM. An SVM FC Protocol service must be created before FC Protocol initiators can log in to the SVM.<br/>
The FC Protocol service REST API allows you to create, update, delete, and discover FC services for SVMs.
## Performance monitoring
Performance of the SVM can be monitored by the `metric.*` and `statistics.*` properties. These show the performance of the SVM in terms of IOPS, latency, and throughput. The `metric.*` properties denote an average whereas `statistics.*` properties denote a real-time monotonically increasing value aggregated across all nodes.
## Examples
### Creating an FC Protocol service for an SVM
The simplest way to create an FC Protocol service is to specify only the SVM, either by name or UUID. By default, the new FC Protocol service is enabled.<br/>
In this example, the `return_records` query parameter is used to retrieve the new FC Protocol service object in the REST response.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcpService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FcpService()
    resource.svm = {"name": "svm1"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
FcpService(
    {
        "enabled": True,
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/5c659d90-c01a-11e8-88ed-005056bbb24b"}
            },
            "uuid": "5c659d90-c01a-11e8-88ed-005056bbb24b",
            "name": "svm1",
        },
        "target": {"name": "20:00:00:50:56:bb:b2:4b"},
        "_links": {
            "self": {
                "href": "/api/protocols/san/fcp/services/5c659d90-c01a-11e8-88ed-005056bbb24b"
            }
        },
    }
)

```
</div>
</div>

---
### Retrieving FC Protocol services for all SVMs in the cluster
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcpService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(FcpService.get_collection()))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    FcpService(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/5c659d90-c01a-11e8-88ed-005056bbb24b"
                    }
                },
                "uuid": "5c659d90-c01a-11e8-88ed-005056bbb24b",
                "name": "svm1",
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/san/fcp/services/5c659d90-c01a-11e8-88ed-005056bbb24b"
                }
            },
        }
    ),
    FcpService(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/6011f874-c01a-11e8-88ed-005056bbb24b"
                    }
                },
                "uuid": "6011f874-c01a-11e8-88ed-005056bbb24b",
                "name": "svm2",
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/san/fcp/services/6011f874-c01a-11e8-88ed-005056bbb24b"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving details for a specific FC Protocol service
The FC Protocol service is identified by the UUID of its SVM.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcpService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FcpService(**{"svm.uuid": "5c659d90-c01a-11e8-88ed-005056bbb24b"})
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
FcpService(
    {
        "enabled": True,
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/5c659d90-c01a-11e8-88ed-005056bbb24b"}
            },
            "uuid": "5c659d90-c01a-11e8-88ed-005056bbb24b",
            "name": "svm1",
        },
        "target": {"name": "20:00:00:50:56:bb:b2:4b"},
        "_links": {
            "self": {
                "href": "/api/protocols/san/fcp/services/5c659d90-c01a-11e8-88ed-005056bbb24b"
            }
        },
    }
)

```
</div>
</div>

---
### Disabling an FC Protocol service
Disabling an FC Protocol service shuts down all active FC Protocol logins for the SVM and prevents new FC Protocol logins.<br/>
The FC Protocol service to update is identified by the UUID of its SVM.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcpService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FcpService(**{"svm.uuid": "5c659d90-c01a-11e8-88ed-005056bbb24b"})
    resource.enabled = False
    resource.patch()

```

<br/>
You can retrieve the FC Protocol service to confirm the change.<br/>
In this example, the `fields` query parameter is used to limit the response to the `enabled` property and FC Protocol service identifiers.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcpService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FcpService(**{"svm.uuid": "5c659d90-c01a-11e8-88ed-005056bbb24b"})
    resource.get(fields="enabled")
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
FcpService(
    {
        "enabled": False,
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/5c659d90-c01a-11e8-88ed-005056bbb24b"}
            },
            "uuid": "5c659d90-c01a-11e8-88ed-005056bbb24b",
            "name": "svm1",
        },
        "_links": {
            "self": {
                "href": "/api/protocols/san/fcp/services/5c659d90-c01a-11e8-88ed-005056bbb24b"
            }
        },
    }
)

```
</div>
</div>

---
### Deleting an FC Protocol service
The FC Protocol service must be disabled before it can be deleted.<br/>
The FC Protocol service to delete is identified by the UUID of its SVM.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcpService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FcpService(**{"svm.uuid": "5c659d90-c01a-11e8-88ed-005056bbb24b"})
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


__all__ = ["FcpService", "FcpServiceSchema"]
__pdoc__ = {
    "FcpServiceSchema.resource": False,
    "FcpService.fcp_service_show": False,
    "FcpService.fcp_service_create": False,
    "FcpService.fcp_service_modify": False,
    "FcpService.fcp_service_delete": False,
}


class FcpServiceSchema(ResourceSchema):
    """The fields of the FcpService object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the fcp_service. """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" The administrative state of the FC Protocol service. The FC Protocol service can be disabled to block all FC Protocol connectivity to the SVM.<br/>
This is optional in POST and PATCH. The default setting is _true_ (enabled) in POST. """

    metric = fields.Nested("netapp_ontap.models.performance_metric_svm.PerformanceMetricSvmSchema", data_key="metric", unknown=EXCLUDE)
    r""" The metric field of the fcp_service. """

    statistics = fields.Nested("netapp_ontap.models.performance_metric_raw_svm.PerformanceMetricRawSvmSchema", data_key="statistics", unknown=EXCLUDE)
    r""" The statistics field of the fcp_service. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the fcp_service. """

    target = fields.Nested("netapp_ontap.models.fcp_service_target.FcpServiceTargetSchema", data_key="target", unknown=EXCLUDE)
    r""" The target field of the fcp_service. """

    @property
    def resource(self):
        return FcpService

    gettable_fields = [
        "links",
        "enabled",
        "metric.links",
        "metric.duration",
        "metric.iops",
        "metric.latency",
        "metric.status",
        "metric.throughput",
        "metric.timestamp",
        "statistics.iops_raw",
        "statistics.latency_raw",
        "statistics.status",
        "statistics.throughput_raw",
        "statistics.timestamp",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "target",
    ]
    """links,enabled,metric.links,metric.duration,metric.iops,metric.latency,metric.status,metric.throughput,metric.timestamp,statistics.iops_raw,statistics.latency_raw,statistics.status,statistics.throughput_raw,statistics.timestamp,svm.links,svm.name,svm.uuid,target,"""

    patchable_fields = [
        "enabled",
        "metric.iops",
        "metric.latency",
        "metric.throughput",
        "statistics.iops_raw",
        "statistics.latency_raw",
        "statistics.throughput_raw",
        "svm.name",
        "svm.uuid",
        "target",
    ]
    """enabled,metric.iops,metric.latency,metric.throughput,statistics.iops_raw,statistics.latency_raw,statistics.throughput_raw,svm.name,svm.uuid,target,"""

    postable_fields = [
        "enabled",
        "metric.iops",
        "metric.latency",
        "metric.throughput",
        "statistics.iops_raw",
        "statistics.latency_raw",
        "statistics.throughput_raw",
        "svm.name",
        "svm.uuid",
        "target",
    ]
    """enabled,metric.iops,metric.latency,metric.throughput,statistics.iops_raw,statistics.latency_raw,statistics.throughput_raw,svm.name,svm.uuid,target,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FcpService.get_collection(fields=field)]
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
            raise NetAppRestError("FcpService modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FcpService(Resource):
    r""" A Fibre Channel (FC) Protocol service defines the properties of the FC Protocol target for an SVM. There can be at most one FC Protocol service for an SVM. An SVM's FC Protocol service must be created before FC Protocol initiators can login to the SVM.<br/>
A FC Protocol service is identified by the UUID of its SVM. """

    _schema = FcpServiceSchema
    _path = "/api/protocols/san/fcp/services"
    _keys = ["svm.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves FC Protocol services.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `vserver fcp show`
### Learn more
* [`DOC /protocols/san/fcp/services`](#docs-SAN-protocols_san_fcp_services)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fcp service show")
        def fcp_service_show(
            fields: List[Choices.define(["enabled", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of FcpService resources

            Args:
                enabled: The administrative state of the FC Protocol service. The FC Protocol service can be disabled to block all FC Protocol connectivity to the SVM.<br/> This is optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return FcpService.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all FcpService resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["FcpService"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an FC Protocol service.
### Related ONTAP commands
* `vserver fcp modify`
* `vserver fcp start`
* `vserver fcp stop`
### Learn more
* [`DOC /protocols/san/fcp/services`](#docs-SAN-protocols_san_fcp_services)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["FcpService"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["FcpService"], NetAppResponse]:
        r"""Creates an FC Protocol service.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the FC Protocol service.
### Related ONTAP commands
* `vserver fcp create`
### Learn more
* [`DOC /protocols/san/fcp/services`](#docs-SAN-protocols_san_fcp_services)
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
        records: Iterable["FcpService"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an FC Protocol service. An FC Protocol service must be disabled before it can be deleted.
### Related ONTAP commands
* `vserver fcp delete`
### Learn more
* [`DOC /protocols/san/fcp/services`](#docs-SAN-protocols_san_fcp_services)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves FC Protocol services.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `vserver fcp show`
### Learn more
* [`DOC /protocols/san/fcp/services`](#docs-SAN-protocols_san_fcp_services)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an FC Protocol service.
### Related ONTAP commands
* `vserver fcp show`
### Learn more
* [`DOC /protocols/san/fcp/services`](#docs-SAN-protocols_san_fcp_services)
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
        r"""Creates an FC Protocol service.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the FC Protocol service.
### Related ONTAP commands
* `vserver fcp create`
### Learn more
* [`DOC /protocols/san/fcp/services`](#docs-SAN-protocols_san_fcp_services)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fcp service create")
        async def fcp_service_create(
        ) -> ResourceTable:
            """Create an instance of a FcpService resource

            Args:
                links: 
                enabled: The administrative state of the FC Protocol service. The FC Protocol service can be disabled to block all FC Protocol connectivity to the SVM.<br/> This is optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
                metric: 
                statistics: 
                svm: 
                target: 
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
            if target is not None:
                kwargs["target"] = target

            resource = FcpService(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create FcpService: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an FC Protocol service.
### Related ONTAP commands
* `vserver fcp modify`
* `vserver fcp start`
* `vserver fcp stop`
### Learn more
* [`DOC /protocols/san/fcp/services`](#docs-SAN-protocols_san_fcp_services)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fcp service modify")
        async def fcp_service_modify(
        ) -> ResourceTable:
            """Modify an instance of a FcpService resource

            Args:
                enabled: The administrative state of the FC Protocol service. The FC Protocol service can be disabled to block all FC Protocol connectivity to the SVM.<br/> This is optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
                query_enabled: The administrative state of the FC Protocol service. The FC Protocol service can be disabled to block all FC Protocol connectivity to the SVM.<br/> This is optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
            """

            kwargs = {}
            changes = {}
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled

            if enabled is not None:
                changes["enabled"] = enabled

            if hasattr(FcpService, "find"):
                resource = FcpService.find(
                    **kwargs
                )
            else:
                resource = FcpService()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify FcpService: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an FC Protocol service. An FC Protocol service must be disabled before it can be deleted.
### Related ONTAP commands
* `vserver fcp delete`
### Learn more
* [`DOC /protocols/san/fcp/services`](#docs-SAN-protocols_san_fcp_services)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fcp service delete")
        async def fcp_service_delete(
        ) -> None:
            """Delete an instance of a FcpService resource

            Args:
                enabled: The administrative state of the FC Protocol service. The FC Protocol service can be disabled to block all FC Protocol connectivity to the SVM.<br/> This is optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled

            if hasattr(FcpService, "find"):
                resource = FcpService.find(
                    **kwargs
                )
            else:
                resource = FcpService()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete FcpService: %s" % err)


