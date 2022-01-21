r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

### Retrieving all monitored files
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import MonitoredFile

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(MonitoredFile.get_collection()))

```

### Provisioning a monitored file
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import MonitoredFile

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = MonitoredFile()
    resource.svm = {"name": "vs0"}
    resource.volume = {"name": "vol1"}
    resource.path = "/a/b/c/file.txt"
    resource.post(hydrate=True)
    print(resource)

```

### Removing a file from the monitored files list
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import MonitoredFile

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = MonitoredFile(uuid="6f68c85b-45e1-11e9-8fc7-005056bbc848")
    resource.delete()

```

### Alternate method for removing files from the monitored files list
Monitored files can also be deleted via a combination of any of (uuid, svm.name, svm.uuid, volume.name, volume.uuid, path).
For example, to remove all monitored-files from monitoring in a single svm named vs0, use the following
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import MonitoredFile

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = MonitoredFile()
    resource.delete(**{"svm.name": "vs0"})

```

## Performance monitoring
Performance of the monitored file can be monitored by the `metric.*` and `statistics.*` properties. These fields show the performance of the monitored file in terms of IOPS, latency and throughput. The `metric.*` properties denote an average whereas `statistics.*` properties denote a real-time monotonically increasing value aggregated across all nodes.
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


__all__ = ["MonitoredFile", "MonitoredFileSchema"]
__pdoc__ = {
    "MonitoredFileSchema.resource": False,
    "MonitoredFile.monitored_file_show": False,
    "MonitoredFile.monitored_file_create": False,
    "MonitoredFile.monitored_file_modify": False,
    "MonitoredFile.monitored_file_delete": False,
}


class MonitoredFileSchema(ResourceSchema):
    """The fields of the MonitoredFile object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the monitored_file. """

    metric = fields.Nested("netapp_ontap.resources.performance_metric.PerformanceMetricSchema", data_key="metric", unknown=EXCLUDE)
    r""" The metric field of the monitored_file. """

    path = fields.Str(
        data_key="path",
    )
    r""" Path of the file to be monitored.

Example: /a/b/c/file.txt """

    statistics = fields.Nested("netapp_ontap.models.performance_metric_raw.PerformanceMetricRawSchema", data_key="statistics", unknown=EXCLUDE)
    r""" The statistics field of the monitored_file. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the monitored_file. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" Unique identifier created for identifying the file that is monitored.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the monitored_file. """

    @property
    def resource(self):
        return MonitoredFile

    gettable_fields = [
        "links",
        "metric",
        "path",
        "statistics.iops_raw",
        "statistics.latency_raw",
        "statistics.status",
        "statistics.throughput_raw",
        "statistics.timestamp",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,metric,path,statistics.iops_raw,statistics.latency_raw,statistics.status,statistics.throughput_raw,statistics.timestamp,svm.links,svm.name,svm.uuid,uuid,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "path",
    ]
    """path,"""

    postable_fields = [
        "path",
        "svm.name",
        "svm.uuid",
        "volume.name",
        "volume.uuid",
    ]
    """path,svm.name,svm.uuid,volume.name,volume.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in MonitoredFile.get_collection(fields=field)]
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
            raise NetAppRestError("MonitoredFile modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class MonitoredFile(Resource):
    """Allows interaction with MonitoredFile objects on the host"""

    _schema = MonitoredFileSchema
    _path = "/api/storage/monitored-files"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves all monitored files.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
* `metric.*`
### Learn more
* [`DOC /storage/monitored-files`](#docs-storage-storage_monitored-files)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="monitored file show")
        def monitored_file_show(
            fields: List[Choices.define(["path", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of MonitoredFile resources

            Args:
                path: Path of the file to be monitored.
                uuid: Unique identifier created for identifying the file that is monitored.
            """

            kwargs = {}
            if path is not None:
                kwargs["path"] = path
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return MonitoredFile.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all MonitoredFile resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["MonitoredFile"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["MonitoredFile"], NetAppResponse]:
        r"""Creates a monitored file.
### Required properties
The required properties take the following options:
  - path and volume.uuid or
  - path and (svm.name or svm.uuid) and volume.name
* `path` - Path to the file to be monitored.
* `volume.uuid` - Volume where the file to be monitored exists
* `svm.name` or `svm.uuid` - SVM where the file to be monitored exists
* `volume.name` - Volume where the file to be monitored exists.
### Learn more
* [`DOC /storage/monitored-files`](#docs-storage-storage_monitored-files)
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
        records: Iterable["MonitoredFile"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Removes the file from the list of monitored files.
### Learn more
* [`DOC /storage/monitored-files`](#docs-storage-storage_monitored-files)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves all monitored files.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
* `metric.*`
### Learn more
* [`DOC /storage/monitored-files`](#docs-storage-storage_monitored-files)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)


    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates a monitored file.
### Required properties
The required properties take the following options:
  - path and volume.uuid or
  - path and (svm.name or svm.uuid) and volume.name
* `path` - Path to the file to be monitored.
* `volume.uuid` - Volume where the file to be monitored exists
* `svm.name` or `svm.uuid` - SVM where the file to be monitored exists
* `volume.name` - Volume where the file to be monitored exists.
### Learn more
* [`DOC /storage/monitored-files`](#docs-storage-storage_monitored-files)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="monitored file create")
        async def monitored_file_create(
        ) -> ResourceTable:
            """Create an instance of a MonitoredFile resource

            Args:
                links: 
                metric: 
                path: Path of the file to be monitored.
                statistics: 
                svm: 
                uuid: Unique identifier created for identifying the file that is monitored.
                volume: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if metric is not None:
                kwargs["metric"] = metric
            if path is not None:
                kwargs["path"] = path
            if statistics is not None:
                kwargs["statistics"] = statistics
            if svm is not None:
                kwargs["svm"] = svm
            if uuid is not None:
                kwargs["uuid"] = uuid
            if volume is not None:
                kwargs["volume"] = volume

            resource = MonitoredFile(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create MonitoredFile: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Removes the file from the list of monitored files.
### Learn more
* [`DOC /storage/monitored-files`](#docs-storage-storage_monitored-files)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="monitored file delete")
        async def monitored_file_delete(
        ) -> None:
            """Delete an instance of a MonitoredFile resource

            Args:
                path: Path of the file to be monitored.
                uuid: Unique identifier created for identifying the file that is monitored.
            """

            kwargs = {}
            if path is not None:
                kwargs["path"] = path
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(MonitoredFile, "find"):
                resource = MonitoredFile.find(
                    **kwargs
                )
            else:
                resource = MonitoredFile()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete MonitoredFile: %s" % err)


