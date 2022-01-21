r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
An iSCSI service defines the properties of the iSCSI target for an SVM. There can be at most one iSCSI service for an SVM. An SVM's iSCSI service must be created before iSCSI initiators can log in to the SVM.<br/>
The iSCSI service REST API allows you to create, update, delete, and discover iSCSI services for SVMs.
## Performance monitoring
Performance of the SVM can be monitored by the `metric.*` and `statistics.*` properties. These show the performance of the SVM in terms of IOPS, latency and throughput. The `metric.*` properties denote an average whereas `statistics.*` properties denote a real-time monotonically increasing value aggregated across all nodes.
## Examples
### Creating an iSCSI service for an SVM
The simplest way to create an iSCSI service is to specify only the SVM, either by name or UUID. By default, the new iSCSI service is enabled and uses the SVM name as its target alias.<br/>
In this example, the `return_records` query parameter is used to retrieve the new iSCSI service object in the REST response.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import IscsiService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = IscsiService()
    resource.svm = {"name": "svm1"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
IscsiService(
    {
        "enabled": True,
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/19d04b8e-94d7-11e8-8370-005056b48fd2"}
            },
            "uuid": "19d04b8e-94d7-11e8-8370-005056b48fd2",
            "name": "svm1",
        },
        "target": {
            "name": "iqn.1992-08.com.netapp:sn.19d04b8e94d711e88370005056b48fd2:vs.4",
            "alias": "svm1",
        },
        "_links": {
            "self": {
                "href": "/api/protocols/san/iscsi/services/19d04b8e-94d7-11e8-8370-005056b48fd2"
            }
        },
    }
)

```
</div>
</div>

---
### Retrieving the iSCSI services for all SVMs in the cluster
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import IscsiService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(IscsiService.get_collection()))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    IscsiService(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/19d04b8e-94d7-11e8-8370-005056b48fd2"
                    }
                },
                "uuid": "19d04b8e-94d7-11e8-8370-005056b48fd2",
                "name": "svm1",
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/san/iscsi/services/19d04b8e-94d7-11e8-8370-005056b48fd2"
                }
            },
        }
    ),
    IscsiService(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/25f617cf-94d7-11e8-8370-005056b48fd2"
                    }
                },
                "uuid": "25f617cf-94d7-11e8-8370-005056b48fd2",
                "name": "svm2",
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/san/iscsi/services/25f617cf-94d7-11e8-8370-005056b48fd2"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving details for a specific iSCSI service
The iSCSI service is identified by the UUID of its SVM.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import IscsiService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = IscsiService(**{"svm.uuid": "19d04b8e-94d7-11e8-8370-005056b48fd2"})
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
IscsiService(
    {
        "enabled": True,
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/19d04b8e-94d7-11e8-8370-005056b48fd2"}
            },
            "uuid": "19d04b8e-94d7-11e8-8370-005056b48fd2",
            "name": "svm1",
        },
        "target": {
            "name": "iqn.1992-08.com.netapp:sn.19d04b8e94d711e88370005056b48fd2:vs.4",
            "alias": "svm1",
        },
        "_links": {
            "self": {
                "href": "/api/protocols/san/iscsi/services/19d04b8e-94d7-11e8-8370-005056b48fd2"
            }
        },
    }
)

```
</div>
</div>

---
### Disabling an iSCSI service
Disabling an iSCSI service shuts down all active iSCSI sessions for the SVM and prevents the creation of new iSCSI sessions.<br/>
The iSCSI service to update is identified by the UUID of its SVM.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import IscsiService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = IscsiService(**{"svm.uuid": "19d04b8e-94d7-11e8-8370-005056b48fd2"})
    resource.enabled = False
    resource.patch()

```

<br/>
You can retrieve the iSCSI service to confirm the change.<br/>
In this example, the `fields` query parameter is used to limit the response to the `enabled` property and iSCSI service identifiers.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import IscsiService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = IscsiService(**{"svm.uuid": "19d04b8e-94d7-11e8-8370-005056b48fd2"})
    resource.get(fields="enabled")
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
IscsiService(
    {
        "enabled": False,
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/19d04b8e-94d7-11e8-8370-005056b48fd2"}
            },
            "uuid": "19d04b8e-94d7-11e8-8370-005056b48fd2",
            "name": "svm1",
        },
        "_links": {
            "self": {
                "href": "/api/protocols/san/iscsi/services/19d04b8e-94d7-11e8-8370-005056b48fd2"
            }
        },
    }
)

```
</div>
</div>

---
### Deleting an iSCSI service
The iSCSI service must be disabled before it can be deleted.<br/>
The iSCSI service to be deleted is identified by the UUID of its SVM.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import IscsiService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = IscsiService(**{"svm.uuid": "19d04b8e-94d7-11e8-8370-005056b48fd2"})
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


__all__ = ["IscsiService", "IscsiServiceSchema"]
__pdoc__ = {
    "IscsiServiceSchema.resource": False,
    "IscsiService.iscsi_service_show": False,
    "IscsiService.iscsi_service_create": False,
    "IscsiService.iscsi_service_modify": False,
    "IscsiService.iscsi_service_delete": False,
}


class IscsiServiceSchema(ResourceSchema):
    """The fields of the IscsiService object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the iscsi_service. """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" The administrative state of the iSCSI service. The iSCSI service can be disabled to block all iSCSI connectivity to the SVM.<br/>
Optional in POST and PATCH. The default setting is _true_ (enabled) in POST. """

    metric = fields.Nested("netapp_ontap.models.performance_metric_svm.PerformanceMetricSvmSchema", data_key="metric", unknown=EXCLUDE)
    r""" The metric field of the iscsi_service. """

    statistics = fields.Nested("netapp_ontap.models.performance_metric_raw_svm.PerformanceMetricRawSvmSchema", data_key="statistics", unknown=EXCLUDE)
    r""" The statistics field of the iscsi_service. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the iscsi_service. """

    target = fields.Nested("netapp_ontap.models.iscsi_service_target.IscsiServiceTargetSchema", data_key="target", unknown=EXCLUDE)
    r""" The target field of the iscsi_service. """

    @property
    def resource(self):
        return IscsiService

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
        return [getattr(r, field) for r in IscsiService.get_collection(fields=field)]
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
            raise NetAppRestError("IscsiService modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class IscsiService(Resource):
    r""" An iSCSI service defines the properties of the iSCSI target for an SVM. There can be at most one iSCSI service for an SVM. An SVM's iSCSI service must be created before iSCSI initiators can log in to the SVM.<br/>
An iSCSI service is identified by the UUID of its SVM. """

    _schema = IscsiServiceSchema
    _path = "/api/protocols/san/iscsi/services"
    _keys = ["svm.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves iSCSI services.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `vserver iscsi show`
### Learn more
* [`DOC /protocols/san/iscsi/services`](#docs-SAN-protocols_san_iscsi_services)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="iscsi service show")
        def iscsi_service_show(
            fields: List[Choices.define(["enabled", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of IscsiService resources

            Args:
                enabled: The administrative state of the iSCSI service. The iSCSI service can be disabled to block all iSCSI connectivity to the SVM.<br/> Optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return IscsiService.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all IscsiService resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["IscsiService"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an iSCSI service.
### Related ONTAP commands
* `vserver iscsi modify`
* `vserver iscsi start`
* `vserver iscsi stop`
### Learn more
* [`DOC /protocols/san/iscsi/services`](#docs-SAN-protocols_san_iscsi_services)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["IscsiService"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["IscsiService"], NetAppResponse]:
        r"""Creates an iSCSI service.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the iSCSI service.
### Related ONTAP commands
* `vserver iscsi create`
### Learn more
* [`DOC /protocols/san/iscsi/services`](#docs-SAN-protocols_san_iscsi_services)
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
        records: Iterable["IscsiService"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an iSCSI service. An iSCSI service must be disabled before it can be deleted.
### Related ONTAP commands
* `vserver iscsi delete`
### Learn more
* [`DOC /protocols/san/iscsi/services`](#docs-SAN-protocols_san_iscsi_services)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves iSCSI services.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `vserver iscsi show`
### Learn more
* [`DOC /protocols/san/iscsi/services`](#docs-SAN-protocols_san_iscsi_services)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an iSCSI service.
### Related ONTAP commands
* `vserver iscsi show`
### Learn more
* [`DOC /protocols/san/iscsi/services`](#docs-SAN-protocols_san_iscsi_services)
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
        r"""Creates an iSCSI service.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the iSCSI service.
### Related ONTAP commands
* `vserver iscsi create`
### Learn more
* [`DOC /protocols/san/iscsi/services`](#docs-SAN-protocols_san_iscsi_services)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="iscsi service create")
        async def iscsi_service_create(
        ) -> ResourceTable:
            """Create an instance of a IscsiService resource

            Args:
                links: 
                enabled: The administrative state of the iSCSI service. The iSCSI service can be disabled to block all iSCSI connectivity to the SVM.<br/> Optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
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

            resource = IscsiService(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create IscsiService: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an iSCSI service.
### Related ONTAP commands
* `vserver iscsi modify`
* `vserver iscsi start`
* `vserver iscsi stop`
### Learn more
* [`DOC /protocols/san/iscsi/services`](#docs-SAN-protocols_san_iscsi_services)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="iscsi service modify")
        async def iscsi_service_modify(
        ) -> ResourceTable:
            """Modify an instance of a IscsiService resource

            Args:
                enabled: The administrative state of the iSCSI service. The iSCSI service can be disabled to block all iSCSI connectivity to the SVM.<br/> Optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
                query_enabled: The administrative state of the iSCSI service. The iSCSI service can be disabled to block all iSCSI connectivity to the SVM.<br/> Optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
            """

            kwargs = {}
            changes = {}
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled

            if enabled is not None:
                changes["enabled"] = enabled

            if hasattr(IscsiService, "find"):
                resource = IscsiService.find(
                    **kwargs
                )
            else:
                resource = IscsiService()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify IscsiService: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an iSCSI service. An iSCSI service must be disabled before it can be deleted.
### Related ONTAP commands
* `vserver iscsi delete`
### Learn more
* [`DOC /protocols/san/iscsi/services`](#docs-SAN-protocols_san_iscsi_services)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="iscsi service delete")
        async def iscsi_service_delete(
        ) -> None:
            """Delete an instance of a IscsiService resource

            Args:
                enabled: The administrative state of the iSCSI service. The iSCSI service can be disabled to block all iSCSI connectivity to the SVM.<br/> Optional in POST and PATCH. The default setting is _true_ (enabled) in POST. 
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled

            if hasattr(IscsiService, "find"):
                resource = IscsiService.find(
                    **kwargs
                )
            else:
                resource = IscsiService()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete IscsiService: %s" % err)


