r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Auditing for NAS events is a security measure that enables you to track and log certain CIFS and NFS events on storage virtual machines (SVMs). This helps you track potential security problems and provides evidence of any security breaches.
## Examples
---
### Creating an audit entry with log rotation size and log retention count
To create an audit entry with log rotation size and log retention count, use the following API. Note the <i>return_records=true</i> query parameter is used to obtain the newly created entry in the response.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Audit

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Audit()
    resource.enabled = True
    resource.events = {
        "authorization_policy": False,
        "cap_staging": False,
        "cifs_logon_logoff": True,
        "file_operations": True,
        "file_share": False,
        "security_group": False,
        "user_account": False,
    }
    resource.guarantee = True
    resource.log = {
        "format": "evtx",
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
Audit(
    {
        "enabled": True,
        "log": {
            "rotation": {"size": 2048000},
            "format": "evtx",
            "retention": {"count": 10, "duration": "0s"},
        },
        "log_path": "/",
        "svm": {"uuid": "ec650e97-156e-11e9-abcb-005056bbd0bf", "name": "vs1"},
        "guarantee": True,
        "events": {
            "file_share": False,
            "authorization_policy": False,
            "user_account": False,
            "cap_staging": False,
            "cifs_logon_logoff": True,
            "security_group": False,
            "file_operations": True,
        },
    }
)

```
</div>
</div>

---
### Creating an audit entry with log rotation schedule and log retention duration
To create an audit entry with log rotation schedule and log retention duration, use the following API. Note that the <i>return_records=true</i> query parameter is used to obtain the newly created entry in the response.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Audit

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Audit()
    resource.enabled = False
    resource.events = {
        "authorization_policy": False,
        "cap_staging": False,
        "cifs_logon_logoff": True,
        "file_operations": True,
        "file_share": False,
        "security_group": False,
        "user_account": False,
    }
    resource.guarantee = True
    resource.log = {
        "format": "xml",
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
Audit(
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
            "format": "xml",
            "retention": {"count": 0, "duration": "P4DT12H30M5S"},
        },
        "log_path": "/",
        "svm": {"uuid": "a8d64674-13fc-11e9-87b1-005056a7ae7e", "name": "vs3"},
        "guarantee": True,
        "events": {
            "file_share": False,
            "authorization_policy": False,
            "user_account": False,
            "cap_staging": False,
            "cifs_logon_logoff": True,
            "security_group": False,
            "file_operations": True,
        },
    }
)

```
</div>
</div>

---
### Retrieving an audit configuration for all SVMs in the cluster
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Audit

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(Audit.get_collection(fields="*", return_timeout=15)))

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    Audit(
        {
            "enabled": True,
            "log": {
                "rotation": {"size": 2048000},
                "format": "evtx",
                "retention": {"count": 10, "duration": "0s"},
            },
            "log_path": "/",
            "svm": {"uuid": "ec650e97-156e-11e9-abcb-005056bbd0bf", "name": "vs1"},
            "guarantee": True,
            "events": {
                "file_share": False,
                "authorization_policy": False,
                "user_account": False,
                "cap_staging": False,
                "cifs_logon_logoff": True,
                "security_group": False,
                "file_operations": True,
            },
        }
    ),
    Audit(
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
                "format": "xml",
                "retention": {"count": 0, "duration": "P4DT12H30M5S"},
            },
            "log_path": "/",
            "svm": {"uuid": "a8d64674-13fc-11e9-87b1-005056a7ae7e", "name": "vs3"},
            "guarantee": True,
            "events": {
                "file_share": False,
                "authorization_policy": False,
                "user_account": False,
                "cap_staging": False,
                "cifs_logon_logoff": True,
                "security_group": False,
                "file_operations": True,
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving specific entries with event list as cifs-logon-logoff, file-ops = true for an SVM
The configuration returned is identified by the events in the list of audit configurations for an SVM.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Audit

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            Audit.get_collection(
                return_timeout=15,
                **{"events.file_operations": "true", "events.cifs_logon_logoff": "true"}
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
    Audit(
        {
            "svm": {"uuid": "ec650e97-156e-11e9-abcb-005056bbd0bf", "name": "vs1"},
            "events": {"cifs_logon_logoff": True, "file_operations": True},
        }
    ),
    Audit(
        {
            "svm": {"uuid": "a8d64674-13fc-11e9-87b1-005056a7ae7e", "name": "vs3"},
            "events": {"cifs_logon_logoff": True, "file_operations": True},
        }
    ),
]

```
</div>
</div>

---
### Retrieving a specific audit configuration for an SVM
The configuration returned is identified by the UUID of its SVM.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Audit

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Audit(**{"svm.uuid": "ec650e97-156e-11e9-abcb-005056bbd0bf"})
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
Audit(
    {
        "enabled": True,
        "log": {
            "rotation": {"size": 2048000},
            "format": "evtx",
            "retention": {"count": 10, "duration": "0s"},
        },
        "log_path": "/",
        "svm": {"uuid": "ec650e97-156e-11e9-abcb-005056bbd0bf", "name": "vs1"},
        "guarantee": True,
        "events": {
            "file_share": False,
            "authorization_policy": False,
            "user_account": False,
            "cap_staging": False,
            "cifs_logon_logoff": True,
            "security_group": False,
            "file_operations": True,
        },
    }
)

```
</div>
</div>

---
### Updating a specific audit configuration of an SVM
The configuration is identified by the UUID of its SVM and the provided information is updated.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Audit

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Audit(**{"svm.uuid": "ec650e97-156e-11e9-abcb-005056bbd0bf"})
    resource.enabled = False
    resource.patch()

```

---
### Deleting a specific audit configuration for an SVM
The entry to be deleted is identified by the UUID of its SVM.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Audit

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Audit(**{"svm.uuid": "ec650e97-156e-11e9-abcb-005056bbd0bf"})
    resource.delete(force=True)

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


__all__ = ["Audit", "AuditSchema"]
__pdoc__ = {
    "AuditSchema.resource": False,
    "Audit.audit_show": False,
    "Audit.audit_create": False,
    "Audit.audit_modify": False,
    "Audit.audit_delete": False,
}


class AuditSchema(ResourceSchema):
    """The fields of the Audit object"""

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Specifies whether or not auditing is enabled on the SVM. """

    events = fields.Nested("netapp_ontap.models.audit_events.AuditEventsSchema", data_key="events", unknown=EXCLUDE)
    r""" The events field of the audit. """

    guarantee = fields.Boolean(
        data_key="guarantee",
    )
    r""" Indicates whether there is a strict Guarantee of Auditing

Example: false """

    log = fields.Nested("netapp_ontap.models.log.LogSchema", data_key="log", unknown=EXCLUDE)
    r""" The log field of the audit. """

    log_path = fields.Str(
        data_key="log_path",
    )
    r""" The audit log destination path where consolidated audit logs are stored. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the audit. """

    @property
    def resource(self):
        return Audit

    gettable_fields = [
        "enabled",
        "events",
        "guarantee",
        "log",
        "log_path",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """enabled,events,guarantee,log,log_path,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "enabled",
        "events",
        "guarantee",
        "log",
        "log_path",
        "svm.name",
        "svm.uuid",
    ]
    """enabled,events,guarantee,log,log_path,svm.name,svm.uuid,"""

    postable_fields = [
        "enabled",
        "events",
        "guarantee",
        "log",
        "log_path",
        "svm.name",
        "svm.uuid",
    ]
    """enabled,events,guarantee,log,log_path,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Audit.get_collection(fields=field)]
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
            raise NetAppRestError("Audit modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Audit(Resource):
    r""" Auditing for NAS events is a security measure that enables you to track and log certain CIFS and NFS events on SVMs. """

    _schema = AuditSchema
    _path = "/api/protocols/audit"
    _keys = ["svm.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves audit configurations.
### Related ONTAP commands
* `vserver audit show`
### Learn more
* [`DOC /protocols/audit`](#docs-NAS-protocols_audit)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="audit show")
        def audit_show(
            fields: List[Choices.define(["enabled", "guarantee", "log_path", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of Audit resources

            Args:
                enabled: Specifies whether or not auditing is enabled on the SVM.
                guarantee: Indicates whether there is a strict Guarantee of Auditing
                log_path: The audit log destination path where consolidated audit logs are stored.
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if guarantee is not None:
                kwargs["guarantee"] = guarantee
            if log_path is not None:
                kwargs["log_path"] = log_path
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return Audit.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Audit resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["Audit"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an audit configuration for an SVM.
### Related ONTAP commands
* `vserver audit modify`
### Learn more
* [`DOC /protocols/audit`](#docs-NAS-protocols_audit)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["Audit"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["Audit"], NetAppResponse]:
        r"""Creates an audit configuration.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM to which audit configuration is to be created.
* `log_path` - Path in the owning SVM namespace that is used to store audit logs.
### Default property values
If not specified in POST, the following default property values are assigned:
* `enabled` - _true_
* `events.authorization_policy` - _false_
* `events.cap_staging` - _false_
* `events.file_share` - _false_
* `events.security_group` - _false_
* `events.user_account` - _false_
* `events.cifs_logon_logoff` - _true_
* `events.file_operations` - _true_
* `log.format` - _evtx_
* `log.retention.count` - _0_
* `log.retention.duration` - _PT0S_
* `log.rotation.size` - _100MB_
* `log.rotation.now` - _false_
* `guarantee` - _true_
### Related ONTAP commands
* `vserver audit create`
* `vserver audit enable`
### Learn more
* [`DOC /protocols/audit`](#docs-NAS-protocols_audit)
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
        records: Iterable["Audit"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an audit configuration.
### Related ONTAP commands
* `vserver audit disable`
* `vserver audit delete`
### Learn more
* [`DOC /protocols/audit`](#docs-NAS-protocols_audit)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves audit configurations.
### Related ONTAP commands
* `vserver audit show`
### Learn more
* [`DOC /protocols/audit`](#docs-NAS-protocols_audit)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an audit configuration for an SVM.
### Related ONTAP commands
* `vserver audit show`
### Learn more
* [`DOC /protocols/audit`](#docs-NAS-protocols_audit)
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
        r"""Creates an audit configuration.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM to which audit configuration is to be created.
* `log_path` - Path in the owning SVM namespace that is used to store audit logs.
### Default property values
If not specified in POST, the following default property values are assigned:
* `enabled` - _true_
* `events.authorization_policy` - _false_
* `events.cap_staging` - _false_
* `events.file_share` - _false_
* `events.security_group` - _false_
* `events.user_account` - _false_
* `events.cifs_logon_logoff` - _true_
* `events.file_operations` - _true_
* `log.format` - _evtx_
* `log.retention.count` - _0_
* `log.retention.duration` - _PT0S_
* `log.rotation.size` - _100MB_
* `log.rotation.now` - _false_
* `guarantee` - _true_
### Related ONTAP commands
* `vserver audit create`
* `vserver audit enable`
### Learn more
* [`DOC /protocols/audit`](#docs-NAS-protocols_audit)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="audit create")
        async def audit_create(
        ) -> ResourceTable:
            """Create an instance of a Audit resource

            Args:
                enabled: Specifies whether or not auditing is enabled on the SVM.
                events: 
                guarantee: Indicates whether there is a strict Guarantee of Auditing
                log: 
                log_path: The audit log destination path where consolidated audit logs are stored.
                svm: 
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if events is not None:
                kwargs["events"] = events
            if guarantee is not None:
                kwargs["guarantee"] = guarantee
            if log is not None:
                kwargs["log"] = log
            if log_path is not None:
                kwargs["log_path"] = log_path
            if svm is not None:
                kwargs["svm"] = svm

            resource = Audit(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create Audit: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an audit configuration for an SVM.
### Related ONTAP commands
* `vserver audit modify`
### Learn more
* [`DOC /protocols/audit`](#docs-NAS-protocols_audit)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="audit modify")
        async def audit_modify(
        ) -> ResourceTable:
            """Modify an instance of a Audit resource

            Args:
                enabled: Specifies whether or not auditing is enabled on the SVM.
                query_enabled: Specifies whether or not auditing is enabled on the SVM.
                guarantee: Indicates whether there is a strict Guarantee of Auditing
                query_guarantee: Indicates whether there is a strict Guarantee of Auditing
                log_path: The audit log destination path where consolidated audit logs are stored.
                query_log_path: The audit log destination path where consolidated audit logs are stored.
            """

            kwargs = {}
            changes = {}
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_guarantee is not None:
                kwargs["guarantee"] = query_guarantee
            if query_log_path is not None:
                kwargs["log_path"] = query_log_path

            if enabled is not None:
                changes["enabled"] = enabled
            if guarantee is not None:
                changes["guarantee"] = guarantee
            if log_path is not None:
                changes["log_path"] = log_path

            if hasattr(Audit, "find"):
                resource = Audit.find(
                    **kwargs
                )
            else:
                resource = Audit()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify Audit: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an audit configuration.
### Related ONTAP commands
* `vserver audit disable`
* `vserver audit delete`
### Learn more
* [`DOC /protocols/audit`](#docs-NAS-protocols_audit)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="audit delete")
        async def audit_delete(
        ) -> None:
            """Delete an instance of a Audit resource

            Args:
                enabled: Specifies whether or not auditing is enabled on the SVM.
                guarantee: Indicates whether there is a strict Guarantee of Auditing
                log_path: The audit log destination path where consolidated audit logs are stored.
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if guarantee is not None:
                kwargs["guarantee"] = guarantee
            if log_path is not None:
                kwargs["log_path"] = log_path

            if hasattr(Audit, "find"):
                resource = Audit.find(
                    **kwargs
                )
            else:
                resource = Audit()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete Audit: %s" % err)


