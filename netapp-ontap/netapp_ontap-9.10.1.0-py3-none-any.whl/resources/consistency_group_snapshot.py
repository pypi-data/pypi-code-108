r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Consistency groups support Snapshot copy create, inventory, and restore. Snapshot copies can be created on a specified schedule or on-demand. On-demand Snapshot copies can have a type of application consistent or crash consistent. Crash consistent is the default. Scheduled Snapshot copiess are always crash consistent. There is no functional difference in ONTAP between crash consistent or application consistent Snapshot copies.
<br>The functionality provided by these APIs is not integrated with the host application. Snapshot copies have limited value without host coordination, so the use of the SnapCenter Backup Management suite is recommended to ensure correct interaction between host applications and ONTAP.
### On-Demand Snapshot Copies
A manual Snapshot copy may be created on-demand for a parent consistency group and for any of the children consistency groups within it.
<br> Scheduled and manual Snapshot copy creation operations are subject to a pre-defined seven second internal timeout. If the Snapshot copy creation operation does not complete within this time, it is aborted.
<br> Individual volume Snapshot copies within a consistency group Snapshot copies can be accessed and used with native volume Snapshot copy operations.
<br> When an individual volume Snapshot copy is deleted that is part of a consistency group Snapshot copy, then that consistency group Snapshot copy becomes invalid and which cannot be used for restoring the consistency group.
### Restoring to a Previous Snapshot Copy
A Snapshot copy restores to a parent consistency group from an existing parent consistency group's Snapshot copy.  A Snapshot copy restores to any of the children's consistency groups within it from an existing children's consistency group. Granular Snapshot copies are supported. This is performed by a PATCH operation on the specific consistency group for the restore. An example is shown in [`PATCH /application/consistency-groups`](#/application/consistency_group_modify).
<br> Any existing Snapshot copies that were created chronologically after the time of the Snapshot copy used in a successful restore operation is deleted, in compliance with existing ONTAP "future-snapshot" handling principles.
<br> On failures during consistency group restores, any volumes that have been restored will remain so and will not be rolled back. The user must retry the failed restore operation until it is successful. The user can retry with consistency group restore or individual volume-granular restore.
## Consistency group Snapshot APIs
The following APIs are used to perform operations related to consistency group Snapshot copies:

* GET       /api/application/consistency-groups/snapshots
* POST      /api/application/consistency-groups/snapshots
* GET       /api/application/consistency-groups/snapshots/{uuid}
* DELETE    /api/application/consistency-groups/snapshots/{uuid}
## Examples
### Required properties

* `consistency_group.uuid` - Existing consistency group UUID in which to create the Snapshot copy.
### Retrieving the list of existing Snapshot copies for a consistency group
Retrieves the list of consistency group granluar Snapshot copies for a specific consistency group.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroupSnapshot

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="netapp1!", verify=False
):
    print(
        list(
            ConsistencyGroupSnapshot.get_collection(
                "92c6c770-17a1-11eb-b141-005056acd498"
            )
        )
    )

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    ConsistencyGroupSnapshot(
        {
            "uuid": "92c6c770-17a1-11eb-b141-005056acd498",
            "name": "sa3s1",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/a8d0626a-17a0-11eb-b141-005056acd498/snapshots/92c6c770-17a1-11eb-b141-005056acd498"
                }
            },
        }
    ),
    ConsistencyGroupSnapshot(
        {
            "uuid": "c5a250ba-17a1-11eb-b141-005056acd498",
            "name": "sa3s2",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/a8d0626a-17a0-11eb-b141-005056acd498/snapshots/c5a250ba-17a1-11eb-b141-005056acd498"
                }
            },
        }
    ),
]

```
</div>
</div>

### Retrieves details of a specific Snapshot copy for a consistency group
Retrieves details for a specific Snapshot copy in a consistency group.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroupSnapshot

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="netapp1!", verify=False
):
    resource = ConsistencyGroupSnapshot(
        "92c6c770-17a1-11eb-b141-005056acd498",
        uuid="a175c021-4199-11ec-8674-005056accf3f",
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
ConsistencyGroupSnapshot(
    {
        "consistency_group": {
            "uuid": "ddabc6a5-4196-11ec-8674-005056accf3f",
            "name": "CG_1",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/ddabc6a5-4196-11ec-8674-005056accf3f"
                }
            },
        },
        "consistency_type": "crash",
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/7379fecb-4195-11ec-8674-005056accf3f"}
            },
            "uuid": "7379fecb-4195-11ec-8674-005056accf3f",
            "name": "vs1",
        },
        "uuid": "a175c021-4199-11ec-8674-005056accf3f",
        "create_time": "2021-11-09T15:14:23-05:00",
        "comment": "manually created snapshot",
        "name": "sa3s2",
        "_links": {
            "self": {
                "href": "/api/application/consistency-groups/ddabc6a5-4196-11ec-8674-005056accf3f/snapshots/a175c021-4199-11ec-8674-005056accf3f"
            }
        },
    }
)

```
</div>
</div>

### Creating a crash-consistent Snapshot copy of a consistency group
Creates an on-demand crash-consistent Snapshot copy of an existing consistency group.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroupSnapshot

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="netapp1!", verify=False
):
    resource = ConsistencyGroupSnapshot("a8d0626a-17a0-11eb-b141-005056acd498")
    resource.name = "name_of_this_snapshot"
    resource.consistency_type = "crash"
    resource.comment = "this is a manually created on-demand snapshot"
    resource.snapmirror_label = "my_special_sm_label"
    resource.post(hydrate=True)
    print(resource)

```

### Creating a app-consistent Snapshot copy of a consistency group
Creates an on-demand crash-consistent Snapshot copy of an existing consistency group.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroupSnapshot

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="netapp1!", verify=False
):
    resource = ConsistencyGroupSnapshot("a8d0626a-17a0-11eb-b141-005056acd498")
    resource.name = "name_of_this_snapshot"
    resource.consistency_type = "application"
    resource.comment = "this is a manually created on-demand snapshot"
    resource.snapmirror_label = "my_special_sm_label"
    resource.post(hydrate=True)
    print(resource)

```

### Deleting a Snapshot copy from a consistency group
Deletes an existing Snapshot copy from a consistency group.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroupSnapshot

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="netapp1!", verify=False
):
    resource = ConsistencyGroupSnapshot(
        "a8d0626a-17a0-11eb-b141-005056acd498",
        uuid="92c6c770-17a1-11eb-b141-005056acd498",
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


__all__ = ["ConsistencyGroupSnapshot", "ConsistencyGroupSnapshotSchema"]
__pdoc__ = {
    "ConsistencyGroupSnapshotSchema.resource": False,
    "ConsistencyGroupSnapshot.consistency_group_snapshot_show": False,
    "ConsistencyGroupSnapshot.consistency_group_snapshot_create": False,
    "ConsistencyGroupSnapshot.consistency_group_snapshot_modify": False,
    "ConsistencyGroupSnapshot.consistency_group_snapshot_delete": False,
}


class ConsistencyGroupSnapshotSchema(ResourceSchema):
    """The fields of the ConsistencyGroupSnapshot object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the consistency_group_snapshot. """

    comment = fields.Str(
        data_key="comment",
    )
    r""" Comment for the Snapshot copy.


Example: My Snapshot copy comment """

    consistency_group = fields.Nested("netapp_ontap.resources.consistency_group.ConsistencyGroupSchema", data_key="consistency_group", unknown=EXCLUDE)
    r""" The consistency_group field of the consistency_group_snapshot. """

    consistency_type = fields.Str(
        data_key="consistency_type",
        validate=enum_validation(['crash', 'application']),
    )
    r""" Consistency type. This is for categorization purposes only. A Snapshot copy should not be set to 'application consistent' unless the host application is quiesced for the Snapshot copy. Valid in POST.


Valid choices:

* crash
* application """

    create_time = ImpreciseDateTime(
        data_key="create_time",
    )
    r""" Time the snapshot copy was created


Example: 2020-10-25T11:20:00.000+0000 """

    is_partial = fields.Boolean(
        data_key="is_partial",
    )
    r""" Indicates whether the Snapshot copy taken is partial or not.


Example: false """

    missing_volumes = fields.List(fields.Nested("netapp_ontap.resources.volume.VolumeSchema", unknown=EXCLUDE), data_key="missing_volumes")
    r""" List of volumes which are not in the Snapshot copy. """

    name = fields.Str(
        data_key="name",
    )
    r""" Name of the Snapshot copy. """

    snapmirror_label = fields.Str(
        data_key="snapmirror_label",
    )
    r""" Snapmirror Label for the Snapshot copy.


Example: sm_label """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The SVM in which the consistency group is located. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The unique identifier of the Snapshot copy. The UUID is generated
by ONTAP when the Snapshot copy is created.


Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return ConsistencyGroupSnapshot

    gettable_fields = [
        "links",
        "comment",
        "consistency_group.links",
        "consistency_group.name",
        "consistency_group.uuid",
        "consistency_type",
        "create_time",
        "is_partial",
        "missing_volumes",
        "name",
        "snapmirror_label",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
    ]
    """links,comment,consistency_group.links,consistency_group.name,consistency_group.uuid,consistency_type,create_time,is_partial,missing_volumes,name,snapmirror_label,svm.links,svm.name,svm.uuid,uuid,"""

    patchable_fields = [
        "consistency_group.links",
        "consistency_group.name",
        "consistency_group.uuid",
        "consistency_type",
        "name",
        "svm.name",
        "svm.uuid",
    ]
    """consistency_group.links,consistency_group.name,consistency_group.uuid,consistency_type,name,svm.name,svm.uuid,"""

    postable_fields = [
        "comment",
        "consistency_group.links",
        "consistency_group.name",
        "consistency_group.uuid",
        "consistency_type",
        "name",
        "snapmirror_label",
        "svm.name",
        "svm.uuid",
    ]
    """comment,consistency_group.links,consistency_group.name,consistency_group.uuid,consistency_type,name,snapmirror_label,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in ConsistencyGroupSnapshot.get_collection(fields=field)]
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
            raise NetAppRestError("ConsistencyGroupSnapshot modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class ConsistencyGroupSnapshot(Resource):
    """Allows interaction with ConsistencyGroupSnapshot objects on the host"""

    _schema = ConsistencyGroupSnapshotSchema
    _path = "/api/application/consistency-groups/{consistency_group[uuid]}/snapshots"
    _keys = ["consistency_group.uuid", "uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves Snapshot copies for a consistency group.
## Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`DOC Requesting specific fields`](#docs-docs-Requesting-specific-fields) to learn more.
* `is_partial`
* `missing_voumes.uuid`
* `missing_voumes.name`

### Learn more
* [`DOC /application/consistency-groups/{consistency_group.uuid}/snapshots`](#docs-application-application_consistency-groups_{consistency_group.uuid}_snapshots)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="consistency group snapshot show")
        def consistency_group_snapshot_show(
            consistency_group_uuid,
            comment: Choices.define(_get_field_list("comment"), cache_choices=True, inexact=True)=None,
            consistency_type: Choices.define(_get_field_list("consistency_type"), cache_choices=True, inexact=True)=None,
            create_time: Choices.define(_get_field_list("create_time"), cache_choices=True, inexact=True)=None,
            is_partial: Choices.define(_get_field_list("is_partial"), cache_choices=True, inexact=True)=None,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            snapmirror_label: Choices.define(_get_field_list("snapmirror_label"), cache_choices=True, inexact=True)=None,
            uuid: Choices.define(_get_field_list("uuid"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["comment", "consistency_type", "create_time", "is_partial", "name", "snapmirror_label", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of ConsistencyGroupSnapshot resources

            Args:
                comment: Comment for the Snapshot copy. 
                consistency_type: Consistency type. This is for categorization purposes only. A Snapshot copy should not be set to 'application consistent' unless the host application is quiesced for the Snapshot copy. Valid in POST. 
                create_time: Time the snapshot copy was created 
                is_partial: Indicates whether the Snapshot copy taken is partial or not. 
                name: Name of the Snapshot copy. 
                snapmirror_label: Snapmirror Label for the Snapshot copy. 
                uuid: The unique identifier of the Snapshot copy. The UUID is generated by ONTAP when the Snapshot copy is created. 
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if consistency_type is not None:
                kwargs["consistency_type"] = consistency_type
            if create_time is not None:
                kwargs["create_time"] = create_time
            if is_partial is not None:
                kwargs["is_partial"] = is_partial
            if name is not None:
                kwargs["name"] = name
            if snapmirror_label is not None:
                kwargs["snapmirror_label"] = snapmirror_label
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return ConsistencyGroupSnapshot.get_collection(
                consistency_group_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all ConsistencyGroupSnapshot resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["ConsistencyGroupSnapshot"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["ConsistencyGroupSnapshot"], NetAppResponse]:
        r"""Creates a Snapshot copy of an existing consistency group.
### Required properties
* `consistency_group.uuid` - Existing consistency group UUID in which to create the Snapshot copy.

### Learn more
* [`DOC /application/consistency-groups/{consistency_group.uuid}/snapshots`](#docs-application-application_consistency-groups_{consistency_group.uuid}_snapshots)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["ConsistencyGroupSnapshot"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a Snapshot copy of a consistency group.
## Examples

### Learn more
* [`DOC /application/consistency-groups/{consistency_group.uuid}/snapshots`](#docs-application-application_consistency-groups_{consistency_group.uuid}_snapshots)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves Snapshot copies for a consistency group.
## Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`DOC Requesting specific fields`](#docs-docs-Requesting-specific-fields) to learn more.
* `is_partial`
* `missing_voumes.uuid`
* `missing_voumes.name`

### Learn more
* [`DOC /application/consistency-groups/{consistency_group.uuid}/snapshots`](#docs-application-application_consistency-groups_{consistency_group.uuid}_snapshots)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves details of a specific snapshot for a consistency group.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`DOC Requesting specific fields`](#docs-docs-Requesting-specific-fields) to learn more.
* `is_partial`
* `missing_voumes.uuid`
* `missing_voumes.name`

### Learn more
* [`DOC /application/consistency-groups/{consistency_group.uuid}/snapshots`](#docs-application-application_consistency-groups_{consistency_group.uuid}_snapshots)"""
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
        r"""Creates a Snapshot copy of an existing consistency group.
### Required properties
* `consistency_group.uuid` - Existing consistency group UUID in which to create the Snapshot copy.

### Learn more
* [`DOC /application/consistency-groups/{consistency_group.uuid}/snapshots`](#docs-application-application_consistency-groups_{consistency_group.uuid}_snapshots)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="consistency group snapshot create")
        async def consistency_group_snapshot_create(
            consistency_group_uuid,
            links: dict = None,
            comment: str = None,
            consistency_group: dict = None,
            consistency_type: str = None,
            create_time: datetime = None,
            is_partial: bool = None,
            missing_volumes: dict = None,
            name: str = None,
            snapmirror_label: str = None,
            svm: dict = None,
            uuid: str = None,
        ) -> ResourceTable:
            """Create an instance of a ConsistencyGroupSnapshot resource

            Args:
                links: 
                comment: Comment for the Snapshot copy. 
                consistency_group: 
                consistency_type: Consistency type. This is for categorization purposes only. A Snapshot copy should not be set to 'application consistent' unless the host application is quiesced for the Snapshot copy. Valid in POST. 
                create_time: Time the snapshot copy was created 
                is_partial: Indicates whether the Snapshot copy taken is partial or not. 
                missing_volumes: List of volumes which are not in the Snapshot copy. 
                name: Name of the Snapshot copy. 
                snapmirror_label: Snapmirror Label for the Snapshot copy. 
                svm: The SVM in which the consistency group is located. 
                uuid: The unique identifier of the Snapshot copy. The UUID is generated by ONTAP when the Snapshot copy is created. 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if comment is not None:
                kwargs["comment"] = comment
            if consistency_group is not None:
                kwargs["consistency_group"] = consistency_group
            if consistency_type is not None:
                kwargs["consistency_type"] = consistency_type
            if create_time is not None:
                kwargs["create_time"] = create_time
            if is_partial is not None:
                kwargs["is_partial"] = is_partial
            if missing_volumes is not None:
                kwargs["missing_volumes"] = missing_volumes
            if name is not None:
                kwargs["name"] = name
            if snapmirror_label is not None:
                kwargs["snapmirror_label"] = snapmirror_label
            if svm is not None:
                kwargs["svm"] = svm
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = ConsistencyGroupSnapshot(
                consistency_group_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create ConsistencyGroupSnapshot: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a Snapshot copy of a consistency group.
## Examples

### Learn more
* [`DOC /application/consistency-groups/{consistency_group.uuid}/snapshots`](#docs-application-application_consistency-groups_{consistency_group.uuid}_snapshots)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="consistency group snapshot delete")
        async def consistency_group_snapshot_delete(
            consistency_group_uuid,
            comment: str = None,
            consistency_type: str = None,
            create_time: datetime = None,
            is_partial: bool = None,
            name: str = None,
            snapmirror_label: str = None,
            uuid: str = None,
        ) -> None:
            """Delete an instance of a ConsistencyGroupSnapshot resource

            Args:
                comment: Comment for the Snapshot copy. 
                consistency_type: Consistency type. This is for categorization purposes only. A Snapshot copy should not be set to 'application consistent' unless the host application is quiesced for the Snapshot copy. Valid in POST. 
                create_time: Time the snapshot copy was created 
                is_partial: Indicates whether the Snapshot copy taken is partial or not. 
                name: Name of the Snapshot copy. 
                snapmirror_label: Snapmirror Label for the Snapshot copy. 
                uuid: The unique identifier of the Snapshot copy. The UUID is generated by ONTAP when the Snapshot copy is created. 
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if consistency_type is not None:
                kwargs["consistency_type"] = consistency_type
            if create_time is not None:
                kwargs["create_time"] = create_time
            if is_partial is not None:
                kwargs["is_partial"] = is_partial
            if name is not None:
                kwargs["name"] = name
            if snapmirror_label is not None:
                kwargs["snapmirror_label"] = snapmirror_label
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(ConsistencyGroupSnapshot, "find"):
                resource = ConsistencyGroupSnapshot.find(
                    consistency_group_uuid,
                    **kwargs
                )
            else:
                resource = ConsistencyGroupSnapshot(consistency_group_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete ConsistencyGroupSnapshot: %s" % err)


