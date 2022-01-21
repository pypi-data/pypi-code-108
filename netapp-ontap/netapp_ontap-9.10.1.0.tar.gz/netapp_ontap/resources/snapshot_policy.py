r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
In ONTAP, scheduled Snapshot copy creation works based on Snapshot copy policies.
ONTAP provides three cluster-wide Snapshot copy policies: "default", "default-1weekly" and "none".
A Snapshot copy policy can have more than one schedule associated with it.
A Snapshot copy policy can be linked to a storage object and based on the schedule in the policy, Snapshot copies will be created on the object at that interval.
Each schedule in a Snapshot copy policy has a Snapshot copy name prefix attached to it. Every Snapshot copy created using this policy will have this prefix in its name.
There is also a retention count associated with every schedule. This count indicates the maximum number of Snapshot copies that can exist for a given schedule. Once the Snapshot copy count reaches the retention count, on the next create operation, the oldest Snapshot copy is deleted.<br/>
## Snapshot copy policy APIs
The following APIs are used to perform operations related to Snapshot copy policy information:

* POST      /api/storage/snapshot-policies
* GET       /api/storage/snapshot-policies
* GET       /api/storage/snapshot-policies/{uuid}
* PATCH     /api/storage/snapshot-policies/{uuid}
* DELETE    /api/storage/snapshot-policies/{uuid}
## Examples
### Creating a Snapshot copy policy
The POST operation is used to create a Snapshot copy policy with the specified attributes.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SnapshotPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SnapshotPolicy()
    resource.name = "new_policy"
    resource.enabled = True
    resource.comment = "policy comment"
    resource.copies = [{"schedule": {"name": "5min"}, "count": "5", "prefix": "xyz"}]
    resource.svm = {"name": "vs0"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
SnapshotPolicy(
    {
        "enabled": True,
        "copies": [{"count": 5, "schedule": {"name": "5min"}}],
        "svm": {"name": "vs0"},
        "uuid": "a69d8173-450c-11e9-aa44-005056bbc848",
        "comment": "This is a 5min schedule policy",
        "name": "new_policy",
    }
)

```
</div>
</div>

### Retrieving Snapshot copy policy attributes
The GET operation is used to retrieve Snapshot copy policy attributes.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SnapshotPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(SnapshotPolicy.get_collection()))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    SnapshotPolicy(
        {
            "uuid": "0fa7a554-348d-11e9-b55e-005056bbf1c8",
            "name": "spsv0",
            "_links": {
                "self": {
                    "href": "/api/storage/snapshot-policies/0fa7a554-348d-11e9-b55e-005056bbf1c8"
                }
            },
        }
    ),
    SnapshotPolicy(
        {
            "uuid": "3c112527-2fe8-11e9-b55e-005056bbf1c8",
            "name": "default",
            "_links": {
                "self": {
                    "href": "/api/storage/snapshot-policies/3c112527-2fe8-11e9-b55e-005056bbf1c8"
                }
            },
        }
    ),
    SnapshotPolicy(
        {
            "uuid": "3c1c1656-2fe8-11e9-b55e-005056bbf1c8",
            "name": "default-1weekly",
            "_links": {
                "self": {
                    "href": "/api/storage/snapshot-policies/3c1c1656-2fe8-11e9-b55e-005056bbf1c8"
                }
            },
        }
    ),
    SnapshotPolicy(
        {
            "uuid": "3c228b82-2fe8-11e9-b55e-005056bbf1c8",
            "name": "none",
            "_links": {
                "self": {
                    "href": "/api/storage/snapshot-policies/3c228b82-2fe8-11e9-b55e-005056bbf1c8"
                }
            },
        }
    ),
]

```
</div>
</div>

### Retrieving the attributes of a specific Snapshot copy policy
The GET operation is used to retrieve the attributes of a specific Snapshot copy policy.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SnapshotPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SnapshotPolicy(uuid="3c112527-2fe8-11e9-b55e-005056bbf1c8")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
SnapshotPolicy(
    {
        "enabled": True,
        "scope": "cluster",
        "copies": [
            {"count": 6, "schedule": {"name": "hourly"}, "prefix": "hourly"},
            {"count": 2, "schedule": {"name": "daily"}, "prefix": "daily"},
            {"count": 2, "schedule": {"name": "weekly"}, "prefix": "weekly"},
        ],
        "uuid": "3c112527-2fe8-11e9-b55e-005056bbf1c8",
        "comment": "Default policy with hourly, daily & weekly schedules.",
        "name": "default",
        "_links": {
            "self": {
                "href": "/api/storage/snapshot-policies/3c112527-2fe8-11e9-b55e-005056bbf1c8"
            }
        },
    }
)

```
</div>
</div>

### Updating a Snapshot copy policy
The PATCH operation is used to update the specific attributes of a Snapshot copy policy.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SnapshotPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SnapshotPolicy(uuid="ae9e65c4-4506-11e9-aa44-005056bbc848")
    resource.enabled = False
    resource.patch()

```

### Deleting a Snapshot copy policy
The DELETE operation is used to delete a Snapshot copy policy.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SnapshotPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SnapshotPolicy(uuid="ae9e65c4-4506-11e9-aa44-005056bbc848")
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


__all__ = ["SnapshotPolicy", "SnapshotPolicySchema"]
__pdoc__ = {
    "SnapshotPolicySchema.resource": False,
    "SnapshotPolicy.snapshot_policy_show": False,
    "SnapshotPolicy.snapshot_policy_create": False,
    "SnapshotPolicy.snapshot_policy_modify": False,
    "SnapshotPolicy.snapshot_policy_delete": False,
}


class SnapshotPolicySchema(ResourceSchema):
    """The fields of the SnapshotPolicy object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the snapshot_policy. """

    comment = fields.Str(
        data_key="comment",
    )
    r""" A comment associated with the Snapshot copy policy. """

    copies = fields.List(fields.Nested("netapp_ontap.models.snapshot_policy_copies.SnapshotPolicyCopiesSchema", unknown=EXCLUDE), data_key="copies")
    r""" The copies field of the snapshot_policy. """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Is the Snapshot copy policy enabled?

Example: true """

    name = fields.Str(
        data_key="name",
    )
    r""" Name of the Snapshot copy policy.

Example: default """

    scope = fields.Str(
        data_key="scope",
        validate=enum_validation(['svm', 'cluster']),
    )
    r""" Set to "svm" when the request is on a data SVM, otherwise set to "cluster".

Valid choices:

* svm
* cluster """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the snapshot_policy. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The uuid field of the snapshot_policy.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return SnapshotPolicy

    gettable_fields = [
        "links",
        "comment",
        "copies",
        "enabled",
        "name",
        "scope",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
    ]
    """links,comment,copies,enabled,name,scope,svm.links,svm.name,svm.uuid,uuid,"""

    patchable_fields = [
        "comment",
        "enabled",
    ]
    """comment,enabled,"""

    postable_fields = [
        "comment",
        "copies",
        "enabled",
        "name",
        "svm.name",
        "svm.uuid",
    ]
    """comment,copies,enabled,name,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SnapshotPolicy.get_collection(fields=field)]
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
            raise NetAppRestError("SnapshotPolicy modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SnapshotPolicy(Resource):
    r""" The Snapshot copy policy object is associated with a read-write volume used to create and delete Snapshot copies at regular intervals. """

    _schema = SnapshotPolicySchema
    _path = "/api/storage/snapshot-policies"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of Snapshot copy policies.
### Related ONTAP commands
* `snapshot policy show`
### Learn more
* [`DOC /storage/snapshot-policies`](#docs-storage-storage_snapshot-policies)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snapshot policy show")
        def snapshot_policy_show(
            fields: List[Choices.define(["comment", "enabled", "name", "scope", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SnapshotPolicy resources

            Args:
                comment: A comment associated with the Snapshot copy policy.
                enabled: Is the Snapshot copy policy enabled?
                name: Name of the Snapshot copy policy.
                scope: Set to \"svm\" when the request is on a data SVM, otherwise set to \"cluster\".
                uuid: 
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if enabled is not None:
                kwargs["enabled"] = enabled
            if name is not None:
                kwargs["name"] = name
            if scope is not None:
                kwargs["scope"] = scope
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SnapshotPolicy.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SnapshotPolicy resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["SnapshotPolicy"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a Snapshot copy policy
### Related ONTAP commands
* `snapshot policy modify`
* `snapshot policy modify-schedule`
* `snapshot policy add-schedule`
### Learn more
* [`DOC /storage/snapshot-policies`](#docs-storage-storage_snapshot-policies)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["SnapshotPolicy"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["SnapshotPolicy"], NetAppResponse]:
        r"""Creates a Snapshot copy policy.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the Snapshot copy policy.
* `name` - Name for the Snapshot copy policy.
* `copies.schedule` - Schedule at which Snapshot copies are captured on the volume.
* `copies.count` - Number of Snapshot copies to maintain for this schedule.
### Recommended optional properties
* `copies.prefix` - Prefix to use when creating Snapshot copies at regular intervals.
### Default property values
If not specified in POST, the following default property values are assigned:
* `enabled` - _true_
* `copies.prefix` - Value of `schedule.name`
### Related ONTAP commands
* `snapshot policy create`
### Learn more
* [`DOC /storage/snapshot-policies`](#docs-storage-storage_snapshot-policies)
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
        records: Iterable["SnapshotPolicy"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a Snapshot copy policy
### Related ONTAP commands
* `snapshot policy delete`
### Learn more
* [`DOC /storage/snapshot-policies`](#docs-storage-storage_snapshot-policies)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of Snapshot copy policies.
### Related ONTAP commands
* `snapshot policy show`
### Learn more
* [`DOC /storage/snapshot-policies`](#docs-storage-storage_snapshot-policies)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves details of a specific Snapshot copy policy.
### Related ONTAP commands
* `snapshot policy show`
### Learn more
* [`DOC /storage/snapshot-policies`](#docs-storage-storage_snapshot-policies)
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
        r"""Creates a Snapshot copy policy.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the Snapshot copy policy.
* `name` - Name for the Snapshot copy policy.
* `copies.schedule` - Schedule at which Snapshot copies are captured on the volume.
* `copies.count` - Number of Snapshot copies to maintain for this schedule.
### Recommended optional properties
* `copies.prefix` - Prefix to use when creating Snapshot copies at regular intervals.
### Default property values
If not specified in POST, the following default property values are assigned:
* `enabled` - _true_
* `copies.prefix` - Value of `schedule.name`
### Related ONTAP commands
* `snapshot policy create`
### Learn more
* [`DOC /storage/snapshot-policies`](#docs-storage-storage_snapshot-policies)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snapshot policy create")
        async def snapshot_policy_create(
        ) -> ResourceTable:
            """Create an instance of a SnapshotPolicy resource

            Args:
                links: 
                comment: A comment associated with the Snapshot copy policy.
                copies: 
                enabled: Is the Snapshot copy policy enabled?
                name: Name of the Snapshot copy policy.
                scope: Set to \"svm\" when the request is on a data SVM, otherwise set to \"cluster\".
                svm: 
                uuid: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if comment is not None:
                kwargs["comment"] = comment
            if copies is not None:
                kwargs["copies"] = copies
            if enabled is not None:
                kwargs["enabled"] = enabled
            if name is not None:
                kwargs["name"] = name
            if scope is not None:
                kwargs["scope"] = scope
            if svm is not None:
                kwargs["svm"] = svm
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = SnapshotPolicy(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SnapshotPolicy: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a Snapshot copy policy
### Related ONTAP commands
* `snapshot policy modify`
* `snapshot policy modify-schedule`
* `snapshot policy add-schedule`
### Learn more
* [`DOC /storage/snapshot-policies`](#docs-storage-storage_snapshot-policies)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snapshot policy modify")
        async def snapshot_policy_modify(
        ) -> ResourceTable:
            """Modify an instance of a SnapshotPolicy resource

            Args:
                comment: A comment associated with the Snapshot copy policy.
                query_comment: A comment associated with the Snapshot copy policy.
                enabled: Is the Snapshot copy policy enabled?
                query_enabled: Is the Snapshot copy policy enabled?
                name: Name of the Snapshot copy policy.
                query_name: Name of the Snapshot copy policy.
                scope: Set to \"svm\" when the request is on a data SVM, otherwise set to \"cluster\".
                query_scope: Set to \"svm\" when the request is on a data SVM, otherwise set to \"cluster\".
                uuid: 
                query_uuid: 
            """

            kwargs = {}
            changes = {}
            if query_comment is not None:
                kwargs["comment"] = query_comment
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_name is not None:
                kwargs["name"] = query_name
            if query_scope is not None:
                kwargs["scope"] = query_scope
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if comment is not None:
                changes["comment"] = comment
            if enabled is not None:
                changes["enabled"] = enabled
            if name is not None:
                changes["name"] = name
            if scope is not None:
                changes["scope"] = scope
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(SnapshotPolicy, "find"):
                resource = SnapshotPolicy.find(
                    **kwargs
                )
            else:
                resource = SnapshotPolicy()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify SnapshotPolicy: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a Snapshot copy policy
### Related ONTAP commands
* `snapshot policy delete`
### Learn more
* [`DOC /storage/snapshot-policies`](#docs-storage-storage_snapshot-policies)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snapshot policy delete")
        async def snapshot_policy_delete(
        ) -> None:
            """Delete an instance of a SnapshotPolicy resource

            Args:
                comment: A comment associated with the Snapshot copy policy.
                enabled: Is the Snapshot copy policy enabled?
                name: Name of the Snapshot copy policy.
                scope: Set to \"svm\" when the request is on a data SVM, otherwise set to \"cluster\".
                uuid: 
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if enabled is not None:
                kwargs["enabled"] = enabled
            if name is not None:
                kwargs["name"] = name
            if scope is not None:
                kwargs["scope"] = scope
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(SnapshotPolicy, "find"):
                resource = SnapshotPolicy.find(
                    **kwargs
                )
            else:
                resource = SnapshotPolicy()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete SnapshotPolicy: %s" % err)


