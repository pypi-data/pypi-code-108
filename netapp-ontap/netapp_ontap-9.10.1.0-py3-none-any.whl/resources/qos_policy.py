r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Quality of Service Configuration
A QoS policy defines measurable service level objectives (SLOs) that apply to the storage objects with which the policy is associated. There are two types of policies that can be configured: fixed, which defines a fixed SLO, or adaptive which defines a variable SLO for a storage object. Adaptive policies vary the SLO depending on the space usage of the storage object. A policy can be either a fixed policy or an adaptive one, not both.
<br />
Service level objectives include minimum and maximum limits on throughput in terms of IOPS. Only maximum limits can be set in terms of both IOPS and/or throughput (MB/s). A QoS policy can be used to enforce SLOs for multiple storage objects by specifying "capacity_shared" to true. For example, if a QoS policy with "capacity_shared" is set to true and it has maximum_throughput_iops set to 1000, and this policy is assigned to four volumes, then the combined throughput of all four volumes is limited to 1000 IOPS. If "capacity_shared" is set to false then, each storage object will have it's SLOs enforced individually. For example, in the previous case if the same policy was applied to four volumes but with "capacity_shared" set to false, then each of the volumes would be limited to 1000 IOPS individually. Once "capacity_shared" is set, it cannot be modified.
<br />
Adaptive parameters can specify the variable SLOs in terms of IOPS/TB. The actual IOPS enforced on the storage object can be calculated using the allocated space on the storage object. The policies are enforced individually amongst storage objects.
## Examples
### 1) Create a fixed QoS policy
The following example shows how to create a fixed QoS policy to limit throughput for a storage object between 5000 IOPS and 10000 IOPS which has capacity_shared set to false. This QoS policy can be used as a template to apply on multiple storage objects to provide individual SLOs to each object.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QosPolicy

with HostConnection(
    "172.21.69.245", username="admin", password="password", verify=False
):
    resource = QosPolicy()
    resource.fixed = {
        "capacity_shared": False,
        "max_throughput_iops": 10000,
        "min_throughput_iops": 5000,
    }
    resource.name = "qos_policy_5000_to_10000_iops"
    resource.svm = {"name": "vs0"}
    resource.post(hydrate=True, return_timeout=0)
    print(resource)

```

---
### 2) Create an adaptive QoS policy
The following example shows how to create an adaptive QoS policy which provides 5000 IOPS per GB of allocated space for a storage object with a peak of 6000 IOPS. Minimum IOPS regardless of allocated space are 1000 IOPS.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QosPolicy

with HostConnection(
    "172.21.69.245", username="admin", password="password", verify=False
):
    resource = QosPolicy()
    resource.adaptive = {
        "absolute_min_iops": 1000,
        "expected_iops": 5000,
        "expected_iops_allocation": "used_space",
        "peak_iops": 6000,
        "peak_iops_allocation": "allocated_space",
    }
    resource.name = "adaptive_pg_5k_to_6k"
    resource.svm = {"name": "vs0"}
    resource.post(hydrate=True, return_timeout=0)
    print(resource)

```

----
### 3) Update an existing QoS policy
The following example shows how to update SLOs of an existing QoS policy and also rename it.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QosPolicy

with HostConnection(
    "172.21.69.245", username="admin", password="password", verify=False
):
    resource = QosPolicy(uuid="d38bafc0-5a51-11e9-bd5b-005056ac6f1f")
    resource.fixed = {"max_throughput_iops": 15000, "min_throughput_iops": 10000}
    resource.name = "qos_policy_10k_to_15k_iops"
    resource.patch(hydrate=True, return_timeout=0)

```

---
### 4) Delete an existing QoS policy
When a QoS policy is deleted any associations of the policy with a storage objects are also removed.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QosPolicy

with HostConnection(
    "172.21.69.245", username="admin", password="password", verify=False
):
    resource = QosPolicy(uuid="d38bafc0-5a51-11e9-bd5b-005056ac6f1f")
    resource.delete(return_timeout=0)

```

---
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


__all__ = ["QosPolicy", "QosPolicySchema"]
__pdoc__ = {
    "QosPolicySchema.resource": False,
    "QosPolicy.qos_policy_show": False,
    "QosPolicy.qos_policy_create": False,
    "QosPolicy.qos_policy_modify": False,
    "QosPolicy.qos_policy_delete": False,
}


class QosPolicySchema(ResourceSchema):
    """The fields of the QosPolicy object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the qos_policy. """

    adaptive = fields.Nested("netapp_ontap.models.qos_policy_adaptive.QosPolicyAdaptiveSchema", data_key="adaptive", unknown=EXCLUDE)
    r""" The adaptive field of the qos_policy. """

    fixed = fields.Nested("netapp_ontap.models.qos_policy_fixed.QosPolicyFixedSchema", data_key="fixed", unknown=EXCLUDE)
    r""" The fixed field of the qos_policy. """

    name = fields.Str(
        data_key="name",
    )
    r""" Name of the QoS policy.

Example: extreme """

    object_count = Size(
        data_key="object_count",
    )
    r""" Number of objects attached to this policy. """

    pgid = Size(
        data_key="pgid",
    )
    r""" Policy group ID of the QoS policy. """

    policy_class = fields.Str(
        data_key="policy_class",
        validate=enum_validation(['undefined', 'preset', 'user_defined', 'system_defined', 'autovolume', 'load_control']),
    )
    r""" Class of the QoS policy.

Valid choices:

* undefined
* preset
* user_defined
* system_defined
* autovolume
* load_control """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the qos_policy. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The uuid field of the qos_policy.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return QosPolicy

    gettable_fields = [
        "links",
        "adaptive",
        "fixed",
        "name",
        "object_count",
        "pgid",
        "policy_class",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
    ]
    """links,adaptive,fixed,name,object_count,pgid,policy_class,svm.links,svm.name,svm.uuid,uuid,"""

    patchable_fields = [
        "adaptive",
        "fixed",
        "name",
        "svm.name",
        "svm.uuid",
    ]
    """adaptive,fixed,name,svm.name,svm.uuid,"""

    postable_fields = [
        "adaptive",
        "fixed",
        "name",
        "svm.name",
        "svm.uuid",
    ]
    """adaptive,fixed,name,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in QosPolicy.get_collection(fields=field)]
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
            raise NetAppRestError("QosPolicy modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class QosPolicy(Resource):
    """Allows interaction with QosPolicy objects on the host"""

    _schema = QosPolicySchema
    _path = "/api/storage/qos/policies"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of QoS policies.
### Learn more
* [`DOC /storage/qos/policies`](#docs-storage-storage_qos_policies)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="qos policy show")
        def qos_policy_show(
            fields: List[Choices.define(["name", "object_count", "pgid", "policy_class", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of QosPolicy resources

            Args:
                name: Name of the QoS policy.
                object_count: Number of objects attached to this policy.
                pgid: Policy group ID of the QoS policy.
                policy_class: Class of the QoS policy.
                uuid: 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if object_count is not None:
                kwargs["object_count"] = object_count
            if pgid is not None:
                kwargs["pgid"] = pgid
            if policy_class is not None:
                kwargs["policy_class"] = policy_class
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return QosPolicy.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all QosPolicy resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["QosPolicy"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Update a specific QoS policy.
### Related ONTAP commands
* `qos policy-group modify`
* `qos adaptive-policy-group modify`

### Learn more
* [`DOC /storage/qos/policies`](#docs-storage-storage_qos_policies)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["QosPolicy"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["QosPolicy"], NetAppResponse]:
        r"""Creates a QoS policy.
### Required properties
* `svm.uuid` or `svm.name` - The existing SVM owning the QoS policy.
* `name` - The name of the QoS policy.
* `fixed.*` or `adaptive.*` - Either of the fixed or adaptive parameters.
### Default property values
* If `fixed.*` parameters are specified, then capacity.shared is set to false by default.
### Related ONTAP commands
* `qos policy-group create`
* `qos adaptive-policy-group create`

### Learn more
* [`DOC /storage/qos/policies`](#docs-storage-storage_qos_policies)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["QosPolicy"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a QoS policy. All QoS workloads associated with the policy are removed.
### Related ONTAP commands
* `qos policy-group delete`
* `qos adaptive-policy-group delete`

### Learn more
* [`DOC /storage/qos/policies`](#docs-storage-storage_qos_policies)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of QoS policies.
### Learn more
* [`DOC /storage/qos/policies`](#docs-storage-storage_qos_policies)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific QoS policy.
### Related ONTAP commands
* `qos policy-group show`
* `qos adaptive-policy-group show`

### Learn more
* [`DOC /storage/qos/policies`](#docs-storage-storage_qos_policies)"""
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
        r"""Creates a QoS policy.
### Required properties
* `svm.uuid` or `svm.name` - The existing SVM owning the QoS policy.
* `name` - The name of the QoS policy.
* `fixed.*` or `adaptive.*` - Either of the fixed or adaptive parameters.
### Default property values
* If `fixed.*` parameters are specified, then capacity.shared is set to false by default.
### Related ONTAP commands
* `qos policy-group create`
* `qos adaptive-policy-group create`

### Learn more
* [`DOC /storage/qos/policies`](#docs-storage-storage_qos_policies)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="qos policy create")
        async def qos_policy_create(
        ) -> ResourceTable:
            """Create an instance of a QosPolicy resource

            Args:
                links: 
                adaptive: 
                fixed: 
                name: Name of the QoS policy.
                object_count: Number of objects attached to this policy.
                pgid: Policy group ID of the QoS policy.
                policy_class: Class of the QoS policy.
                svm: 
                uuid: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if adaptive is not None:
                kwargs["adaptive"] = adaptive
            if fixed is not None:
                kwargs["fixed"] = fixed
            if name is not None:
                kwargs["name"] = name
            if object_count is not None:
                kwargs["object_count"] = object_count
            if pgid is not None:
                kwargs["pgid"] = pgid
            if policy_class is not None:
                kwargs["policy_class"] = policy_class
            if svm is not None:
                kwargs["svm"] = svm
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = QosPolicy(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create QosPolicy: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Update a specific QoS policy.
### Related ONTAP commands
* `qos policy-group modify`
* `qos adaptive-policy-group modify`

### Learn more
* [`DOC /storage/qos/policies`](#docs-storage-storage_qos_policies)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="qos policy modify")
        async def qos_policy_modify(
        ) -> ResourceTable:
            """Modify an instance of a QosPolicy resource

            Args:
                name: Name of the QoS policy.
                query_name: Name of the QoS policy.
                object_count: Number of objects attached to this policy.
                query_object_count: Number of objects attached to this policy.
                pgid: Policy group ID of the QoS policy.
                query_pgid: Policy group ID of the QoS policy.
                policy_class: Class of the QoS policy.
                query_policy_class: Class of the QoS policy.
                uuid: 
                query_uuid: 
            """

            kwargs = {}
            changes = {}
            if query_name is not None:
                kwargs["name"] = query_name
            if query_object_count is not None:
                kwargs["object_count"] = query_object_count
            if query_pgid is not None:
                kwargs["pgid"] = query_pgid
            if query_policy_class is not None:
                kwargs["policy_class"] = query_policy_class
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if name is not None:
                changes["name"] = name
            if object_count is not None:
                changes["object_count"] = object_count
            if pgid is not None:
                changes["pgid"] = pgid
            if policy_class is not None:
                changes["policy_class"] = policy_class
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(QosPolicy, "find"):
                resource = QosPolicy.find(
                    **kwargs
                )
            else:
                resource = QosPolicy()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify QosPolicy: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a QoS policy. All QoS workloads associated with the policy are removed.
### Related ONTAP commands
* `qos policy-group delete`
* `qos adaptive-policy-group delete`

### Learn more
* [`DOC /storage/qos/policies`](#docs-storage-storage_qos_policies)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="qos policy delete")
        async def qos_policy_delete(
        ) -> None:
            """Delete an instance of a QosPolicy resource

            Args:
                name: Name of the QoS policy.
                object_count: Number of objects attached to this policy.
                pgid: Policy group ID of the QoS policy.
                policy_class: Class of the QoS policy.
                uuid: 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if object_count is not None:
                kwargs["object_count"] = object_count
            if pgid is not None:
                kwargs["pgid"] = pgid
            if policy_class is not None:
                kwargs["policy_class"] = policy_class
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(QosPolicy, "find"):
                resource = QosPolicy.find(
                    **kwargs
                )
            else:
                resource = QosPolicy()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete QosPolicy: %s" % err)


