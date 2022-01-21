r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
In ONTAP, scheduled Snapshot copy creation works based on the schedules associated with Snapshot copy policies.
ONTAP provides six cluster-wide schedules: "5min", "8hour", "hourly", "daily", "weekly" and "monthly".
A Snapshot copy policy is created using at least one of these schedules and up to 5 schedules can be associated with a Snapshot copy policy.
A Snapshot copy policy can be linked to a storage object and based on the schedule in the policy, Snapshot copies are created on the object at that interval.
Each schedule in a Snapshot copy policy has a Snapshot copy name prefix attached to it. Every Snapshot copy created using this policy has this prefix in its name.
There is also a retention count associated with every schedule. This count indicates the maximum number of Snapshot copies that can exist for a given schedule.
Once the Snapshot copy count reaches the retention count, on the next create operation, the oldest Snapshot copy is deleted.
A schedule can be added, modified or deleted from a Snapshot copy policy.<br/>
## Snapshot copy policy schedule APIs
The following APIs are used to perform operations related to Snapshot copy policy schedules:

* POST      /api/storage/snapshot-policies/{snapshot_policy.uuid}/schedules/
* GET       /api/storage/snapshot-policies/{snapshot_policy.uuid}/schedules/
* GET       /api/storage/snapshot-policies/{snapshot_policy.uuid}/schedules/{schedule.uuid}
* PATCH     /api/storage/snapshot-policies/{snapshot_policy.uuid}/schedules/{schedule.uuid}
* DELETE    /api/storage/snapshot-policies/{snapshot_policy.uuid}/schedules/{schedule.uuid}
## Examples
### Adding schedule to a Snapshot copy policy
The POST operation is used to create a schedule for a Snapshot copy policy with the specified attributes.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SnapshotPolicySchedule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SnapshotPolicySchedule("32a0841a-818e-11e9-b4f4-005056bbab9c")
    resource.schedule.uuid = "7c985d80-818a-11e9-b4f4-005056bbab9c"
    resource.count = "5"
    resource.prefix = "new_hourly"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
SnapshotPolicySchedule(
    {
        "schedule": {"uuid": "7c985d80-818a-11e9-b4f4-005056bbab9c"},
        "prefix": "new_monthly",
        "count": 5,
        "snapshot_policy": {"uuid": "32a0841a-818e-11e9-b4f4-005056bbab9c"},
    }
)

```
</div>
</div>

### Retrieving Snapshot copy policy schedules
The GET operation is used to retrieve Snapshot copy policy schedules.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SnapshotPolicySchedule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            SnapshotPolicySchedule.get_collection(
                "32a0841a-818e-11e9-b4f4-005056bbab9c"
            )
        )
    )

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    SnapshotPolicySchedule(
        {
            "schedule": {
                "uuid": "63d017dc-818a-11e9-b4f4-005056bbab9c",
                "name": "5min",
            },
            "snapshot_policy": {"uuid": "32a0841a-818e-11e9-b4f4-005056bbab9c"},
        }
    ),
    SnapshotPolicySchedule(
        {
            "schedule": {
                "uuid": "64a5c5da-818a-11e9-b4f4-005056bbab9c",
                "name": "8hour",
            },
            "snapshot_policy": {"uuid": "32a0841a-818e-11e9-b4f4-005056bbab9c"},
        }
    ),
    SnapshotPolicySchedule(
        {
            "schedule": {
                "uuid": "63e21a3e-818a-11e9-b4f4-005056bbab9c",
                "name": "daily",
            },
            "snapshot_policy": {"uuid": "32a0841a-818e-11e9-b4f4-005056bbab9c"},
        }
    ),
    SnapshotPolicySchedule(
        {
            "schedule": {
                "uuid": "7c985d80-818a-11e9-b4f4-005056bbab9c",
                "name": "monthly",
            },
            "snapshot_policy": {"uuid": "32a0841a-818e-11e9-b4f4-005056bbab9c"},
        }
    ),
]

```
</div>
</div>

### Retrieving the attributes of a specific Snapshot copy policy schedule
The GET operation is used to retrieve the attributes of a specific Snapshot copy policy schedule.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SnapshotPolicySchedule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SnapshotPolicySchedule(
        "32a0841a-818e-11e9-b4f4-005056bbab9c",
        **{"schedule.uuid": "7c985d80-818a-11e9-b4f4-005056bbab9c"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
SnapshotPolicySchedule(
    {
        "schedule": {"uuid": "7c985d80-818a-11e9-b4f4-005056bbab9c", "name": "monthly"},
        "prefix": "new_monthly",
        "count": 5,
        "snapshot_policy": {"uuid": "32a0841a-818e-11e9-b4f4-005056bbab9c"},
        "snapmirror_label": "-",
    }
)

```
</div>
</div>

### Updating a Snapshot copy policy schedule
The PATCH operation is used to update the specific attributes of a Snapshot copy policy.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SnapshotPolicySchedule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SnapshotPolicySchedule(
        "32a0841a-818e-11e9-b4f4-005056bbab9c",
        **{"schedule.uuid": "7c985d80-818a-11e9-b4f4-005056bbab9c"}
    )
    resource.count = "10"
    resource.patch()

```

### Deleting a Snapshot copy policy
The DELETE operation is used to delete a Snapshot copy policy.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SnapshotPolicySchedule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SnapshotPolicySchedule(
        "32a0841a-818e-11e9-b4f4-005056bbab9c",
        **{"schedule.uuid": "7c985d80-818a-11e9-b4f4-005056bbab9c"}
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


__all__ = ["SnapshotPolicySchedule", "SnapshotPolicyScheduleSchema"]
__pdoc__ = {
    "SnapshotPolicyScheduleSchema.resource": False,
    "SnapshotPolicySchedule.snapshot_policy_schedule_show": False,
    "SnapshotPolicySchedule.snapshot_policy_schedule_create": False,
    "SnapshotPolicySchedule.snapshot_policy_schedule_modify": False,
    "SnapshotPolicySchedule.snapshot_policy_schedule_delete": False,
}


class SnapshotPolicyScheduleSchema(ResourceSchema):
    """The fields of the SnapshotPolicySchedule object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the snapshot_policy_schedule. """

    count = Size(
        data_key="count",
    )
    r""" The number of Snapshot copies to maintain for this schedule. """

    prefix = fields.Str(
        data_key="prefix",
    )
    r""" The prefix to use while creating Snapshot copies at regular intervals. """

    schedule = fields.Nested("netapp_ontap.resources.schedule.ScheduleSchema", data_key="schedule", unknown=EXCLUDE)
    r""" The schedule field of the snapshot_policy_schedule. """

    snapmirror_label = fields.Str(
        data_key="snapmirror_label",
    )
    r""" Label for SnapMirror operations """

    snapshot_policy = fields.Nested("netapp_ontap.resources.snapshot_policy.SnapshotPolicySchema", data_key="snapshot_policy", unknown=EXCLUDE)
    r""" The snapshot_policy field of the snapshot_policy_schedule. """

    @property
    def resource(self):
        return SnapshotPolicySchedule

    gettable_fields = [
        "links",
        "count",
        "prefix",
        "schedule.links",
        "schedule.name",
        "schedule.uuid",
        "snapmirror_label",
        "snapshot_policy.links",
        "snapshot_policy.name",
        "snapshot_policy.uuid",
    ]
    """links,count,prefix,schedule.links,schedule.name,schedule.uuid,snapmirror_label,snapshot_policy.links,snapshot_policy.name,snapshot_policy.uuid,"""

    patchable_fields = [
        "count",
        "schedule.name",
        "schedule.uuid",
        "snapmirror_label",
        "snapshot_policy.name",
        "snapshot_policy.uuid",
    ]
    """count,schedule.name,schedule.uuid,snapmirror_label,snapshot_policy.name,snapshot_policy.uuid,"""

    postable_fields = [
        "count",
        "prefix",
        "schedule.name",
        "schedule.uuid",
        "snapmirror_label",
        "snapshot_policy.name",
        "snapshot_policy.uuid",
    ]
    """count,prefix,schedule.name,schedule.uuid,snapmirror_label,snapshot_policy.name,snapshot_policy.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SnapshotPolicySchedule.get_collection(fields=field)]
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
            raise NetAppRestError("SnapshotPolicySchedule modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SnapshotPolicySchedule(Resource):
    r""" The Snapshot copy policy schedule object is associated with a Snapshot copy policy and it defines the interval at which Snapshot copies are created and deleted. """

    _schema = SnapshotPolicyScheduleSchema
    _path = "/api/storage/snapshot-policies/{snapshot_policy[uuid]}/schedules"
    _keys = ["snapshot_policy.uuid", "schedule.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of Snapshot copy policy schedules.
### Related ONTAP commands
* `snapshot policy show`
### Learn more
* [`DOC /storage/snapshot-policies/{snapshot_policy.uuid}/schedules`](#docs-storage-storage_snapshot-policies_{snapshot_policy.uuid}_schedules)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snapshot policy schedule show")
        def snapshot_policy_schedule_show(
            snapshot_policy_uuid,
            count: Choices.define(_get_field_list("count"), cache_choices=True, inexact=True)=None,
            prefix: Choices.define(_get_field_list("prefix"), cache_choices=True, inexact=True)=None,
            snapmirror_label: Choices.define(_get_field_list("snapmirror_label"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["count", "prefix", "snapmirror_label", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SnapshotPolicySchedule resources

            Args:
                count: The number of Snapshot copies to maintain for this schedule.
                prefix: The prefix to use while creating Snapshot copies at regular intervals.
                snapmirror_label: Label for SnapMirror operations
            """

            kwargs = {}
            if count is not None:
                kwargs["count"] = count
            if prefix is not None:
                kwargs["prefix"] = prefix
            if snapmirror_label is not None:
                kwargs["snapmirror_label"] = snapmirror_label
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SnapshotPolicySchedule.get_collection(
                snapshot_policy_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SnapshotPolicySchedule resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["SnapshotPolicySchedule"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a Snapshot copy policy schedule
### Related ONTAP commands
* `snapshot policy modify-schedule`
### Learn more
* [`DOC /storage/snapshot-policies/{snapshot_policy.uuid}/schedules`](#docs-storage-storage_snapshot-policies_{snapshot_policy.uuid}_schedules)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["SnapshotPolicySchedule"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["SnapshotPolicySchedule"], NetAppResponse]:
        r"""Adds a schedule to a Snapshot copy policy.
### Required properties
* `schedule.uuid` or `schedule.name` - Schedule at which Snapshot copies are captured on the volume.
* `count` - Number of Snapshot copies to maintain for this schedule.
### Recommended optional properties
* `prefix` - Prefix to use when creating Snapshot copies at regular intervals.
### Default property values
If not specified in POST, the following default property values are assigned:
* `prefix` - Value of `schedule.name`
### Related ONTAP commands
* `snapshot policy add-schedule`
### Learn more
* [`DOC /storage/snapshot-policies/{snapshot_policy.uuid}/schedules`](#docs-storage-storage_snapshot-policies_{snapshot_policy.uuid}_schedules)
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
        records: Iterable["SnapshotPolicySchedule"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a schedule from a Snapshot copy policy
### Related ONTAP commands
* `snapshot policy remove-schedule`
### Learn more
* [`DOC /storage/snapshot-policies/{snapshot_policy.uuid}/schedules`](#docs-storage-storage_snapshot-policies_{snapshot_policy.uuid}_schedules)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of Snapshot copy policy schedules.
### Related ONTAP commands
* `snapshot policy show`
### Learn more
* [`DOC /storage/snapshot-policies/{snapshot_policy.uuid}/schedules`](#docs-storage-storage_snapshot-policies_{snapshot_policy.uuid}_schedules)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves details of a specific Snapshot copy policy schedule.
### Related ONTAP commands
* `snapshot policy show`
### Learn more
* [`DOC /storage/snapshot-policies/{snapshot_policy.uuid}/schedules`](#docs-storage-storage_snapshot-policies_{snapshot_policy.uuid}_schedules)
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
        r"""Adds a schedule to a Snapshot copy policy.
### Required properties
* `schedule.uuid` or `schedule.name` - Schedule at which Snapshot copies are captured on the volume.
* `count` - Number of Snapshot copies to maintain for this schedule.
### Recommended optional properties
* `prefix` - Prefix to use when creating Snapshot copies at regular intervals.
### Default property values
If not specified in POST, the following default property values are assigned:
* `prefix` - Value of `schedule.name`
### Related ONTAP commands
* `snapshot policy add-schedule`
### Learn more
* [`DOC /storage/snapshot-policies/{snapshot_policy.uuid}/schedules`](#docs-storage-storage_snapshot-policies_{snapshot_policy.uuid}_schedules)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snapshot policy schedule create")
        async def snapshot_policy_schedule_create(
            snapshot_policy_uuid,
            links: dict = None,
            count: Size = None,
            prefix: str = None,
            schedule: dict = None,
            snapmirror_label: str = None,
            snapshot_policy: dict = None,
        ) -> ResourceTable:
            """Create an instance of a SnapshotPolicySchedule resource

            Args:
                links: 
                count: The number of Snapshot copies to maintain for this schedule.
                prefix: The prefix to use while creating Snapshot copies at regular intervals.
                schedule: 
                snapmirror_label: Label for SnapMirror operations
                snapshot_policy: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if count is not None:
                kwargs["count"] = count
            if prefix is not None:
                kwargs["prefix"] = prefix
            if schedule is not None:
                kwargs["schedule"] = schedule
            if snapmirror_label is not None:
                kwargs["snapmirror_label"] = snapmirror_label
            if snapshot_policy is not None:
                kwargs["snapshot_policy"] = snapshot_policy

            resource = SnapshotPolicySchedule(
                snapshot_policy_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SnapshotPolicySchedule: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a Snapshot copy policy schedule
### Related ONTAP commands
* `snapshot policy modify-schedule`
### Learn more
* [`DOC /storage/snapshot-policies/{snapshot_policy.uuid}/schedules`](#docs-storage-storage_snapshot-policies_{snapshot_policy.uuid}_schedules)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snapshot policy schedule modify")
        async def snapshot_policy_schedule_modify(
            snapshot_policy_uuid,
            count: Size = None,
            query_count: Size = None,
            prefix: str = None,
            query_prefix: str = None,
            snapmirror_label: str = None,
            query_snapmirror_label: str = None,
        ) -> ResourceTable:
            """Modify an instance of a SnapshotPolicySchedule resource

            Args:
                count: The number of Snapshot copies to maintain for this schedule.
                query_count: The number of Snapshot copies to maintain for this schedule.
                prefix: The prefix to use while creating Snapshot copies at regular intervals.
                query_prefix: The prefix to use while creating Snapshot copies at regular intervals.
                snapmirror_label: Label for SnapMirror operations
                query_snapmirror_label: Label for SnapMirror operations
            """

            kwargs = {}
            changes = {}
            if query_count is not None:
                kwargs["count"] = query_count
            if query_prefix is not None:
                kwargs["prefix"] = query_prefix
            if query_snapmirror_label is not None:
                kwargs["snapmirror_label"] = query_snapmirror_label

            if count is not None:
                changes["count"] = count
            if prefix is not None:
                changes["prefix"] = prefix
            if snapmirror_label is not None:
                changes["snapmirror_label"] = snapmirror_label

            if hasattr(SnapshotPolicySchedule, "find"):
                resource = SnapshotPolicySchedule.find(
                    snapshot_policy_uuid,
                    **kwargs
                )
            else:
                resource = SnapshotPolicySchedule(snapshot_policy_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify SnapshotPolicySchedule: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a schedule from a Snapshot copy policy
### Related ONTAP commands
* `snapshot policy remove-schedule`
### Learn more
* [`DOC /storage/snapshot-policies/{snapshot_policy.uuid}/schedules`](#docs-storage-storage_snapshot-policies_{snapshot_policy.uuid}_schedules)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snapshot policy schedule delete")
        async def snapshot_policy_schedule_delete(
            snapshot_policy_uuid,
            count: Size = None,
            prefix: str = None,
            snapmirror_label: str = None,
        ) -> None:
            """Delete an instance of a SnapshotPolicySchedule resource

            Args:
                count: The number of Snapshot copies to maintain for this schedule.
                prefix: The prefix to use while creating Snapshot copies at regular intervals.
                snapmirror_label: Label for SnapMirror operations
            """

            kwargs = {}
            if count is not None:
                kwargs["count"] = count
            if prefix is not None:
                kwargs["prefix"] = prefix
            if snapmirror_label is not None:
                kwargs["snapmirror_label"] = snapmirror_label

            if hasattr(SnapshotPolicySchedule, "find"):
                resource = SnapshotPolicySchedule.find(
                    snapshot_policy_uuid,
                    **kwargs
                )
            else:
                resource = SnapshotPolicySchedule(snapshot_policy_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete SnapshotPolicySchedule: %s" % err)


