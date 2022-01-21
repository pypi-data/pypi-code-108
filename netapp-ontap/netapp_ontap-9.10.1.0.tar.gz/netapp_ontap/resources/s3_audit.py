r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
S3 events auditing is a security measure that enables you to track and log certain S3 events on storage virtual machines (SVMs). You can track potential security problems and provides evidence of any security breaches.
## Examples
---
### Creating an S3 audit entry with log rotation size and log retention count
To create an S3 audit entry with log rotation size and log retention count, use the following API. Note the <i>return_records=true</i> query parameter is used to obtain the newly created entry in the response.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Audit

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Audit("ec650e97-156e-11e9-abcb-005056bbd0bf")
    resource.enabled = True
    resource.events = {"data": False, "management": False}
    resource.log = {
        "format": "json",
        "retention": {"count": 10},
        "rotation": {"size": 2048000},
    }
    resource.log_path = "/"
    resource.svm = {"name": "vs1", "uuid": "ec650e97-156e-11e9-abcb-005056bbd0bf"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
S3Audit(
    {
        "enabled": True,
        "log": {
            "rotation": {"size": 2048000},
            "format": "json",
            "retention": {"count": 10, "duration": "0s"},
        },
        "svm": {"uuid": "ec650e97-156e-11e9-abcb-005056bbd0bf", "name": "vs1"},
        "log_path": "/",
        "events": {"data": False, "management": False},
    }
)

```
</div>
</div>

---
### Creating an S3 audit entry with log rotation schedule and log retention duration
To create an S3 audit entry with log rotation schedule and log retention duration, use the following API. Note that the <i>return_records=true</i> query parameter is used to obtain the newly created entry in the response.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Audit

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Audit("a8d64674-13fc-11e9-87b1-005056a7ae7e")
    resource.enabled = False
    resource.events = {"data": True, "management": True}
    resource.log = {
        "format": "json",
        "retention": {"duration": "P4DT12H30M5S"},
        "rotation": {
            "schedule": {
                "days": [1, 5, 10, 15],
                "hours": [0, 1, 6, 12, 18, 23],
                "minutes": [10, 15, 30, 45, 59],
                "months": [0],
                "weekdays": [0, 2, 5],
            }
        },
    }
    resource.log_path = "/"
    resource.svm = {"name": "vs3", "uuid": "a8d64674-13fc-11e9-87b1-005056a7ae7e"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
S3Audit(
    {
        "enabled": True,
        "log": {
            "rotation": {
                "schedule": {
                    "months": [0],
                    "days": [1, 5, 10, 15],
                    "minutes": [10, 15, 30, 45, 59],
                    "weekdays": [0, 2, 5],
                    "hours": [0, 1, 6, 12, 18, 23],
                }
            },
            "format": "json",
            "retention": {"count": 0, "duration": "P4DT12H30M5S"},
        },
        "svm": {"uuid": "a8d64674-13fc-11e9-87b1-005056a7ae7e", "name": "vs3"},
        "log_path": "/",
        "events": {"data": True, "management": True},
    }
)

```
</div>
</div>

---
### Retrieving an S3 audit configuration for all SVMs in the cluster
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Audit

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Audit("*")
    resource.get(fields="*", return_timeout=15)
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    S3Audit(
        {
            "enabled": True,
            "log": {
                "rotation": {"size": 2048000},
                "format": "json",
                "retention": {"count": 10, "duration": "0s"},
            },
            "svm": {"uuid": "ec650e97-156e-11e9-abcb-005056bbd0bf", "name": "vs1"},
            "log_path": "/",
            "events": {"data": False, "management": False},
        }
    ),
    S3Audit(
        {
            "enabled": True,
            "log": {
                "rotation": {
                    "schedule": {
                        "months": [0],
                        "days": [1, 5, 10, 15],
                        "minutes": [10, 15, 30, 45, 59],
                        "weekdays": [0, 2, 5],
                        "hours": [0, 1, 6, 12, 18, 23],
                    }
                },
                "format": "json",
                "retention": {"count": 0, "duration": "P4DT12H30M5S"},
            },
            "svm": {"uuid": "a8d64674-13fc-11e9-87b1-005056a7ae7e", "name": "vs3"},
            "log_path": "/",
            "events": {"data": True, "management": True},
        }
    ),
]

```
</div>
</div>

---
### Retrieving specific entries with event list as data and management event for an SVM
The configuration returned is identified by the events in the list of S3 audit configurations of an SVM.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Audit

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Audit("*")
    resource.get(
        return_timeout=15, **{"events.data": "true", "events.management": "true"}
    )
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
[
    S3Audit(
        {
            "svm": {"uuid": "ec650e97-156e-11e9-abcb-005056bbd0bf", "name": "vs1"},
            "events": {"data": True, "management": True},
        }
    ),
    S3Audit(
        {
            "svm": {"uuid": "a8d64674-13fc-11e9-87b1-005056a7ae7e", "name": "vs3"},
            "events": {"data": True, "management": True},
        }
    ),
]

```
</div>
</div>

---
### Retrieving a specific S3 audit configuration of an SVM
The configuration returned is identified by the UUID of its SVM.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Audit

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Audit("ec650e97-156e-11e9-abcb-005056bbd0bf")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
S3Audit(
    {
        "enabled": True,
        "log": {
            "rotation": {"size": 2048000},
            "format": "json",
            "retention": {"count": 10, "duration": "0s"},
        },
        "svm": {"uuid": "ec650e97-156e-11e9-abcb-005056bbd0bf", "name": "vs1"},
        "log_path": "/",
        "events": {"data": False, "management": False},
    }
)

```
</div>
</div>

---
### Updating a specific S3 audit configuration of an SVM
The configuration is identified by the UUID of its SVM and the provided information is updated.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Audit

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Audit("ec650e97-156e-11e9-abcb-005056bbd0bf")
    resource.enabled = False
    resource.patch()

```

---
### Deleting a specific S3 audit configuration of an SVM
The entry to be deleted is identified by the UUID of its SVM.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Audit

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Audit("ec650e97-156e-11e9-abcb-005056bbd0bf")
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


__all__ = ["S3Audit", "S3AuditSchema"]
__pdoc__ = {
    "S3AuditSchema.resource": False,
    "S3Audit.s3_audit_show": False,
    "S3Audit.s3_audit_create": False,
    "S3Audit.s3_audit_modify": False,
    "S3Audit.s3_audit_delete": False,
}


class S3AuditSchema(ResourceSchema):
    """The fields of the S3Audit object"""

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Specifies whether or not auditing is enabled on the SVM. """

    events = fields.Nested("netapp_ontap.models.s3_audit_events.S3AuditEventsSchema", data_key="events", unknown=EXCLUDE)
    r""" The events field of the s3_audit. """

    log = fields.Nested("netapp_ontap.models.s3_log.S3LogSchema", data_key="log", unknown=EXCLUDE)
    r""" The log field of the s3_audit. """

    log_path = fields.Str(
        data_key="log_path",
    )
    r""" The audit log destination path where consolidated audit logs are stored. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the s3_audit. """

    @property
    def resource(self):
        return S3Audit

    gettable_fields = [
        "enabled",
        "events",
        "log",
        "log_path",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """enabled,events,log,log_path,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "enabled",
        "events",
        "log",
        "log_path",
    ]
    """enabled,events,log,log_path,"""

    postable_fields = [
        "enabled",
        "events",
        "log",
        "log_path",
        "svm.name",
        "svm.uuid",
    ]
    """enabled,events,log,log_path,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in S3Audit.get_collection(fields=field)]
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
            raise NetAppRestError("S3Audit modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class S3Audit(Resource):
    r""" Auditing for NAS events is a security measure that enables you to track and log certain S3 events on SVMs. """

    _schema = S3AuditSchema
    _path = "/api/protocols/audit/{svm[uuid]}/object-store"
    _keys = ["svm.uuid"]







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves S3 audit configurations.
### Related ONTAP commands
* `vserver object-store-server audit show`
### Learn more
* [`DOC /protocols/audit/{svm.uuid}/object-store`](#docs-NAS-protocols_audit_{svm.uuid}_object-store)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 audit show")
        def s3_audit_show(
            svm_uuid,
            enabled: Choices.define(_get_field_list("enabled"), cache_choices=True, inexact=True)=None,
            log_path: Choices.define(_get_field_list("log_path"), cache_choices=True, inexact=True)=None,
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single S3Audit resource

            Args:
                enabled: Specifies whether or not auditing is enabled on the SVM.
                log_path: The audit log destination path where consolidated audit logs are stored.
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if log_path is not None:
                kwargs["log_path"] = log_path
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = S3Audit(
                svm_uuid,
                **kwargs
            )
            resource.get()
            return [resource]

    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates an S3 audit configuration.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM for which audit configuration is to be created.
* `log_path` - Path in the owning SVM namespace that is used to store audit logs.
### Default property values
If not specified in POST, the following default property values are assigned:
* `enabled` - _true_
* `events.data` - _false_
* `events.management` - _false_
* `log.format` - _json_
* `log.retention.count` - _0_
* `log.retention.duration` - _PT0S_
* `log.rotation.size` - _100MB_
* `log.rotation.now` - _false_
### Related ONTAP commands
* `vserver object-store-server audit create`
* `vserver object-store-server audit enable`
### Learn more
* [`DOC /protocols/audit/{svm.uuid}/object-store`](#docs-NAS-protocols_audit_{svm.uuid}_object-store)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 audit create")
        async def s3_audit_create(
            svm_uuid,
            enabled: bool = None,
            events: dict = None,
            log: dict = None,
            log_path: str = None,
            svm: dict = None,
        ) -> ResourceTable:
            """Create an instance of a S3Audit resource

            Args:
                enabled: Specifies whether or not auditing is enabled on the SVM.
                events: 
                log: 
                log_path: The audit log destination path where consolidated audit logs are stored.
                svm: 
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if events is not None:
                kwargs["events"] = events
            if log is not None:
                kwargs["log"] = log
            if log_path is not None:
                kwargs["log_path"] = log_path
            if svm is not None:
                kwargs["svm"] = svm

            resource = S3Audit(
                svm_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create S3Audit: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an S3 audit configuration for an SVM.
### Related ONTAP commands
* `vserver object-store-server audit modify`
### Learn more
* [`DOC /protocols/audit/{svm.uuid}/object-store`](#docs-NAS-protocols_audit_{svm.uuid}_object-store)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 audit modify")
        async def s3_audit_modify(
            svm_uuid,
            enabled: bool = None,
            query_enabled: bool = None,
            log_path: str = None,
            query_log_path: str = None,
        ) -> ResourceTable:
            """Modify an instance of a S3Audit resource

            Args:
                enabled: Specifies whether or not auditing is enabled on the SVM.
                query_enabled: Specifies whether or not auditing is enabled on the SVM.
                log_path: The audit log destination path where consolidated audit logs are stored.
                query_log_path: The audit log destination path where consolidated audit logs are stored.
            """

            kwargs = {}
            changes = {}
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_log_path is not None:
                kwargs["log_path"] = query_log_path

            if enabled is not None:
                changes["enabled"] = enabled
            if log_path is not None:
                changes["log_path"] = log_path

            if hasattr(S3Audit, "find"):
                resource = S3Audit.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = S3Audit(svm_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify S3Audit: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an S3 audit configuration.
### Related ONTAP commands
* `vserver object-store-server audit disable`
* `vserver object-store-server audit delete`
### Learn more
* [`DOC /protocols/audit/{svm.uuid}/object-store`](#docs-NAS-protocols_audit_{svm.uuid}_object-store)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 audit delete")
        async def s3_audit_delete(
            svm_uuid,
            enabled: bool = None,
            log_path: str = None,
        ) -> None:
            """Delete an instance of a S3Audit resource

            Args:
                enabled: Specifies whether or not auditing is enabled on the SVM.
                log_path: The audit log destination path where consolidated audit logs are stored.
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if log_path is not None:
                kwargs["log_path"] = log_path

            if hasattr(S3Audit, "find"):
                resource = S3Audit.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = S3Audit(svm_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete S3Audit: %s" % err)


