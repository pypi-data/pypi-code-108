r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Use this API to retrieve the status for a specific automatic package update.<p/>
This API supports GET and PATCH calls. PATCH can be used to perform an action on an automatic update.
---
## Examples
### Retrieving the status of an update
The following example shows how to retrieve the status of an automatic update:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AutoUpdateStatus

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AutoUpdateStatus(uuid="440ae2e4-fd8f-4225-9bee-94e2da3f8d9d")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
AutoUpdateStatus(
    {
        "last_state_change_time": "2020-12-01T09:12:23+00:00",
        "content_type": "disk_fw",
        "expiry_time": "2021-06-01T09:12:03+00:00",
        "content_category": "Firmware",
        "status": {
            "code": "8650878",
            "message": "Get-url request to AutoSupport OnDemand Server failed. Error: Couldn't connect to server.",
        },
        "start_time": "2020-12-01T09:12:23+00:00",
        "package_id": "572361f3-e769-439d-9c04-2ba48a08ff47",
        "uuid": "440ae2e4-fd8f-4225-9bee-94e2da3f8d9d",
        "percent_complete": 25,
        "state": "downloading",
        "remaining_time": "PT1M30S",
        "creation_time": "2020-12-01T09:12:03+00:00",
        "description": "disk_fw version 3.0",
        "_links": {"self": {}},
    }
)

```
</div>
</div>

---
### Updating the state of an automatic update
The following example shows how to trigger an automatic update that is waiting for user confirmation:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AutoUpdateStatus

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AutoUpdateStatus(uuid="440ae2e4-fd8f-4225-9bee-94e2da3f8d9d")
    resource.patch(hydrate=True, action="schedule_now")

```

The following example shows how to dismiss an automatic update that is waiting for user confirmation:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AutoUpdateStatus

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AutoUpdateStatus(uuid="440ae2e4-fd8f-4225-9bee-94e2da3f8d9d")
    resource.patch(hydrate=True, action="dismiss")

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


__all__ = ["AutoUpdateStatus", "AutoUpdateStatusSchema"]
__pdoc__ = {
    "AutoUpdateStatusSchema.resource": False,
    "AutoUpdateStatus.auto_update_status_show": False,
    "AutoUpdateStatus.auto_update_status_create": False,
    "AutoUpdateStatus.auto_update_status_modify": False,
    "AutoUpdateStatus.auto_update_status_delete": False,
}


class AutoUpdateStatusSchema(ResourceSchema):
    """The fields of the AutoUpdateStatus object"""

    links = fields.Nested("netapp_ontap.models.application_subsystem_map_object_subsystem_links.ApplicationSubsystemMapObjectSubsystemLinksSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the auto_update_status. """

    action = fields.Str(
        data_key="action",
        validate=enum_validation(['cancel_schedule', 'dismiss', 'schedule', 'schedule_now', 'abort', 'undismiss']),
    )
    r""" Action to be applied to the automatic update.

Valid choices:

* cancel_schedule
* dismiss
* schedule
* schedule_now
* abort
* undismiss """

    content_category = fields.Str(
        data_key="content_category",
    )
    r""" Category of the update

Example: Firmware """

    content_type = fields.Str(
        data_key="content_type",
    )
    r""" Image or package type.

Example: disk_fw """

    creation_time = ImpreciseDateTime(
        data_key="creation_time",
    )
    r""" The date and time at which the update request was received.

Example: 2020-12-01T09:12:23.000+0000 """

    description = fields.Str(
        data_key="description",
    )
    r""" Description of the update.

Example: disk_fw version 3.0 """

    end_time = ImpreciseDateTime(
        data_key="end_time",
    )
    r""" The date and time at which the update request processing ended.

Example: 2020-12-01T09:12:23.000+0000 """

    expiry_time = ImpreciseDateTime(
        data_key="expiry_time",
    )
    r""" The date and time at which the update request will expire.

Example: 2021-06-01T09:12:23.000+0000 """

    last_state_change_time = ImpreciseDateTime(
        data_key="last_state_change_time",
    )
    r""" The date and time at which the state of the update changed last.

Example: 2020-12-01T09:12:23.000+0000 """

    package_id = fields.Str(
        data_key="package_id",
    )
    r""" Unique identifier provided by the back-end.

Example: 572361f3-e769-439d-9c04-2ba48a08ff47 """

    percent_complete = Size(
        data_key="percent_complete",
    )
    r""" Percentage of update completed

Example: 85 """

    remaining_time = fields.Str(
        data_key="remaining_time",
    )
    r""" The time remaining for the update processing to complete in an ISO-8601 duration formatted string.

Example: PT1H45M13S """

    schedule_time = ImpreciseDateTime(
        data_key="schedule_time",
    )
    r""" Date and time when an automatic update action is scheduled.
This field is required when the action field is set to "schedule".


Example: 2020-12-20T21:00:00.000+0000 """

    scheduled_time = ImpreciseDateTime(
        data_key="scheduled_time",
    )
    r""" The date and time at which the update request is currently scheduled for.

Example: 2020-12-05T09:12:23.000+0000 """

    start_time = ImpreciseDateTime(
        data_key="start_time",
    )
    r""" The date and time at which the update request processing started.

Example: 2020-12-01T09:12:23.000+0000 """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['pending_confirmation', 'downloading', 'applying', 'applied', 'dismissed', 'scheduled', 'failed', 'aborted']),
    )
    r""" Current state of the update.

Valid choices:

* pending_confirmation
* downloading
* applying
* applied
* dismissed
* scheduled
* failed
* aborted """

    status = fields.Nested("netapp_ontap.models.error.ErrorSchema", data_key="status", unknown=EXCLUDE)
    r""" The status field of the auto_update_status. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" Unique identifier for this update.

Example: 440ae2e4-fd8f-4225-9bee-94e2da3f9d8d """

    @property
    def resource(self):
        return AutoUpdateStatus

    gettable_fields = [
        "links",
        "content_category",
        "content_type",
        "creation_time",
        "description",
        "end_time",
        "expiry_time",
        "last_state_change_time",
        "package_id",
        "percent_complete",
        "remaining_time",
        "scheduled_time",
        "start_time",
        "state",
        "status",
        "uuid",
    ]
    """links,content_category,content_type,creation_time,description,end_time,expiry_time,last_state_change_time,package_id,percent_complete,remaining_time,scheduled_time,start_time,state,status,uuid,"""

    patchable_fields = [
        "links",
        "action",
        "schedule_time",
    ]
    """links,action,schedule_time,"""

    postable_fields = [
        "links",
    ]
    """links,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in AutoUpdateStatus.get_collection(fields=field)]
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
            raise NetAppRestError("AutoUpdateStatus modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class AutoUpdateStatus(Resource):
    """Allows interaction with AutoUpdateStatus objects on the host"""

    _schema = AutoUpdateStatusSchema
    _path = "/api/support/auto-update/updates"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the status of all updates.

### Learn more
* [`DOC /support/auto-update/updates`](#docs-support-support_auto-update_updates)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="auto update status show")
        def auto_update_status_show(
            fields: List[Choices.define(["action", "content_category", "content_type", "creation_time", "description", "end_time", "expiry_time", "last_state_change_time", "package_id", "percent_complete", "remaining_time", "schedule_time", "scheduled_time", "start_time", "state", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of AutoUpdateStatus resources

            Args:
                action: Action to be applied to the automatic update.
                content_category: Category of the update
                content_type: Image or package type.
                creation_time: The date and time at which the update request was received.
                description: Description of the update.
                end_time: The date and time at which the update request processing ended.
                expiry_time: The date and time at which the update request will expire.
                last_state_change_time: The date and time at which the state of the update changed last.
                package_id: Unique identifier provided by the back-end.
                percent_complete: Percentage of update completed
                remaining_time: The time remaining for the update processing to complete in an ISO-8601 duration formatted string.
                schedule_time: Date and time when an automatic update action is scheduled. This field is required when the action field is set to \"schedule\". 
                scheduled_time: The date and time at which the update request is currently scheduled for.
                start_time: The date and time at which the update request processing started.
                state: Current state of the update.
                uuid: Unique identifier for this update.
            """

            kwargs = {}
            if action is not None:
                kwargs["action"] = action
            if content_category is not None:
                kwargs["content_category"] = content_category
            if content_type is not None:
                kwargs["content_type"] = content_type
            if creation_time is not None:
                kwargs["creation_time"] = creation_time
            if description is not None:
                kwargs["description"] = description
            if end_time is not None:
                kwargs["end_time"] = end_time
            if expiry_time is not None:
                kwargs["expiry_time"] = expiry_time
            if last_state_change_time is not None:
                kwargs["last_state_change_time"] = last_state_change_time
            if package_id is not None:
                kwargs["package_id"] = package_id
            if percent_complete is not None:
                kwargs["percent_complete"] = percent_complete
            if remaining_time is not None:
                kwargs["remaining_time"] = remaining_time
            if schedule_time is not None:
                kwargs["schedule_time"] = schedule_time
            if scheduled_time is not None:
                kwargs["scheduled_time"] = scheduled_time
            if start_time is not None:
                kwargs["start_time"] = start_time
            if state is not None:
                kwargs["state"] = state
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return AutoUpdateStatus.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all AutoUpdateStatus resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["AutoUpdateStatus"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Perform an action on the update.

### Learn more
* [`DOC /support/auto-update/updates/{uuid}`](#docs-support-support_auto-update_updates_{uuid})"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)



    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the status of all updates.

### Learn more
* [`DOC /support/auto-update/updates`](#docs-support-support_auto-update_updates)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the status of an update.

### Learn more
* [`DOC /support/auto-update/updates/{uuid}`](#docs-support-support_auto-update_updates_{uuid})"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)


    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Perform an action on the update.

### Learn more
* [`DOC /support/auto-update/updates/{uuid}`](#docs-support-support_auto-update_updates_{uuid})"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="auto update status modify")
        async def auto_update_status_modify(
        ) -> ResourceTable:
            """Modify an instance of a AutoUpdateStatus resource

            Args:
                action: Action to be applied to the automatic update.
                query_action: Action to be applied to the automatic update.
                content_category: Category of the update
                query_content_category: Category of the update
                content_type: Image or package type.
                query_content_type: Image or package type.
                creation_time: The date and time at which the update request was received.
                query_creation_time: The date and time at which the update request was received.
                description: Description of the update.
                query_description: Description of the update.
                end_time: The date and time at which the update request processing ended.
                query_end_time: The date and time at which the update request processing ended.
                expiry_time: The date and time at which the update request will expire.
                query_expiry_time: The date and time at which the update request will expire.
                last_state_change_time: The date and time at which the state of the update changed last.
                query_last_state_change_time: The date and time at which the state of the update changed last.
                package_id: Unique identifier provided by the back-end.
                query_package_id: Unique identifier provided by the back-end.
                percent_complete: Percentage of update completed
                query_percent_complete: Percentage of update completed
                remaining_time: The time remaining for the update processing to complete in an ISO-8601 duration formatted string.
                query_remaining_time: The time remaining for the update processing to complete in an ISO-8601 duration formatted string.
                schedule_time: Date and time when an automatic update action is scheduled. This field is required when the action field is set to \"schedule\". 
                query_schedule_time: Date and time when an automatic update action is scheduled. This field is required when the action field is set to \"schedule\". 
                scheduled_time: The date and time at which the update request is currently scheduled for.
                query_scheduled_time: The date and time at which the update request is currently scheduled for.
                start_time: The date and time at which the update request processing started.
                query_start_time: The date and time at which the update request processing started.
                state: Current state of the update.
                query_state: Current state of the update.
                uuid: Unique identifier for this update.
                query_uuid: Unique identifier for this update.
            """

            kwargs = {}
            changes = {}
            if query_action is not None:
                kwargs["action"] = query_action
            if query_content_category is not None:
                kwargs["content_category"] = query_content_category
            if query_content_type is not None:
                kwargs["content_type"] = query_content_type
            if query_creation_time is not None:
                kwargs["creation_time"] = query_creation_time
            if query_description is not None:
                kwargs["description"] = query_description
            if query_end_time is not None:
                kwargs["end_time"] = query_end_time
            if query_expiry_time is not None:
                kwargs["expiry_time"] = query_expiry_time
            if query_last_state_change_time is not None:
                kwargs["last_state_change_time"] = query_last_state_change_time
            if query_package_id is not None:
                kwargs["package_id"] = query_package_id
            if query_percent_complete is not None:
                kwargs["percent_complete"] = query_percent_complete
            if query_remaining_time is not None:
                kwargs["remaining_time"] = query_remaining_time
            if query_schedule_time is not None:
                kwargs["schedule_time"] = query_schedule_time
            if query_scheduled_time is not None:
                kwargs["scheduled_time"] = query_scheduled_time
            if query_start_time is not None:
                kwargs["start_time"] = query_start_time
            if query_state is not None:
                kwargs["state"] = query_state
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if action is not None:
                changes["action"] = action
            if content_category is not None:
                changes["content_category"] = content_category
            if content_type is not None:
                changes["content_type"] = content_type
            if creation_time is not None:
                changes["creation_time"] = creation_time
            if description is not None:
                changes["description"] = description
            if end_time is not None:
                changes["end_time"] = end_time
            if expiry_time is not None:
                changes["expiry_time"] = expiry_time
            if last_state_change_time is not None:
                changes["last_state_change_time"] = last_state_change_time
            if package_id is not None:
                changes["package_id"] = package_id
            if percent_complete is not None:
                changes["percent_complete"] = percent_complete
            if remaining_time is not None:
                changes["remaining_time"] = remaining_time
            if schedule_time is not None:
                changes["schedule_time"] = schedule_time
            if scheduled_time is not None:
                changes["scheduled_time"] = scheduled_time
            if start_time is not None:
                changes["start_time"] = start_time
            if state is not None:
                changes["state"] = state
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(AutoUpdateStatus, "find"):
                resource = AutoUpdateStatus.find(
                    **kwargs
                )
            else:
                resource = AutoUpdateStatus()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify AutoUpdateStatus: %s" % err)



