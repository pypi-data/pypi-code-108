r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Quality of Service Workloads
A QoS workload represents a storage object that is tracked by QoS.
<br />
---
## Examples
### Retrieving a list of QoS workloads from the cluster
The following example retrieves all the workloads in the cluster.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QosWorkload

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(QosWorkload.get_collection()))

```

---
### Retrieving a specific QoS workload from the cluster
The following example retrieves a requested workload from the cluster.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QosWorkload

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = QosWorkload(uuid="77b68b1c-a458-11eb-baaa-005056bb873e")
    resource.get()
    print(resource)

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


__all__ = ["QosWorkload", "QosWorkloadSchema"]
__pdoc__ = {
    "QosWorkloadSchema.resource": False,
    "QosWorkload.qos_workload_show": False,
    "QosWorkload.qos_workload_create": False,
    "QosWorkload.qos_workload_modify": False,
    "QosWorkload.qos_workload_delete": False,
}


class QosWorkloadSchema(ResourceSchema):
    """The fields of the QosWorkload object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the qos_workload. """

    file = fields.Str(
        data_key="file",
    )
    r""" Name of the file. """

    lun = fields.Str(
        data_key="lun",
    )
    r""" Name of the LUN. The name of the LUN will be displayed as "(unknown)" if the name cannot be retrieved. """

    name = fields.Str(
        data_key="name",
    )
    r""" Name of the QoS workload.

Example: volume1-wid123 """

    policy = fields.Nested("netapp_ontap.models.qos_policy_group.QosPolicyGroupSchema", data_key="policy", unknown=EXCLUDE)
    r""" The policy field of the qos_workload. """

    qtree = fields.Str(
        data_key="qtree",
    )
    r""" Name of the Qtree. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the qos_workload. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The uuid field of the qos_workload.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    volume = fields.Str(
        data_key="volume",
    )
    r""" Name of the volume. The name of the volume will be displayed as "(unknown)" if the name cannot be retrieved.

Example: volume1 """

    wid = Size(
        data_key="wid",
    )
    r""" Workload ID of the QoS workload.

Example: 123 """

    workload_class = fields.Str(
        data_key="workload_class",
        validate=enum_validation(['undefined', 'preset', 'user_defined', 'system_defined', 'autovolume', 'load_control']),
    )
    r""" Class of the QoS workload.

Valid choices:

* undefined
* preset
* user_defined
* system_defined
* autovolume
* load_control """

    @property
    def resource(self):
        return QosWorkload

    gettable_fields = [
        "links",
        "file",
        "lun",
        "name",
        "policy.links",
        "policy.name",
        "policy.uuid",
        "qtree",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
        "volume",
        "wid",
        "workload_class",
    ]
    """links,file,lun,name,policy.links,policy.name,policy.uuid,qtree,svm.links,svm.name,svm.uuid,uuid,volume,wid,workload_class,"""

    patchable_fields = [
        "name",
        "policy.name",
        "policy.uuid",
        "svm.name",
        "svm.uuid",
    ]
    """name,policy.name,policy.uuid,svm.name,svm.uuid,"""

    postable_fields = [
        "name",
        "policy.name",
        "policy.uuid",
        "svm.name",
        "svm.uuid",
    ]
    """name,policy.name,policy.uuid,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in QosWorkload.get_collection(fields=field)]
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
            raise NetAppRestError("QosWorkload modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class QosWorkload(Resource):
    """Allows interaction with QosWorkload objects on the host"""

    _schema = QosWorkloadSchema
    _path = "/api/storage/qos/workloads"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of QoS workloads.
### Learn more
* [`DOC /storage/qos/workloads`](#docs-storage-storage_qos_workloads)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="qos workload show")
        def qos_workload_show(
            fields: List[Choices.define(["file", "lun", "name", "qtree", "uuid", "volume", "wid", "workload_class", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of QosWorkload resources

            Args:
                file: Name of the file.
                lun: Name of the LUN. The name of the LUN will be displayed as \"(unknown)\" if the name cannot be retrieved.
                name: Name of the QoS workload.
                qtree: Name of the Qtree.
                uuid: 
                volume: Name of the volume. The name of the volume will be displayed as \"(unknown)\" if the name cannot be retrieved.
                wid: Workload ID of the QoS workload.
                workload_class: Class of the QoS workload.
            """

            kwargs = {}
            if file is not None:
                kwargs["file"] = file
            if lun is not None:
                kwargs["lun"] = lun
            if name is not None:
                kwargs["name"] = name
            if qtree is not None:
                kwargs["qtree"] = qtree
            if uuid is not None:
                kwargs["uuid"] = uuid
            if volume is not None:
                kwargs["volume"] = volume
            if wid is not None:
                kwargs["wid"] = wid
            if workload_class is not None:
                kwargs["workload_class"] = workload_class
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return QosWorkload.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all QosWorkload resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of QoS workloads.
### Learn more
* [`DOC /storage/qos/workloads`](#docs-storage-storage_qos_workloads)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific QoS workload.
### Related ONTAP command
* `qos workload show`

### Learn more
* [`DOC /storage/qos/workloads`](#docs-storage-storage_qos_workloads)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)





