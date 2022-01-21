r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
You can use this API to retrieve a list of directories with the most IO activity for a specified volume. Use the `top_metric` parameter to specify which type of IO activity to filter for. This API is used to provide insight into IO activity and supports ordering by IO activity types, namely `iops` and `throughput` metrics. This API supports only returning one IO activity type per request.
## Retrieve a list of the directories with the most IO activity
For a report on the directories with the most IO activity returned in descending order, specify the IO activity type you want to filter for by passing the `iops` or `throughput` property into the top_metric parameter. If the IO activity type is not specified, by default the API returns a list of directories with the greatest number of average read operations per second. The maximum number of directories returned by the API for an IO activity type is 25.

* GET   /api/storage/volumes/{volume.uuid}/top-metrics/directories
## Examples
### Retrieving a list of the directories with the greatest average number of read operations per second:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import TopMetricsDirectory

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            TopMetricsDirectory.get_collection("{volume.uuid}", top_metric="iops.read")
        )
    )

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    TopMetricsDirectory(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/572361f3-e769-439d-9c04-2ba48a08ff43"
                    }
                },
                "uuid": "572361f3-e769-439d-9c04-2ba48a08ff43",
                "name": "vs1",
            },
            "volume": {"name": "vol1"},
            "iops": {"error": {"upper_bound": 1505, "lower_bound": 1495}, "read": 1495},
            "path": "/dir1/dir2",
            "_links": {
                "metadata": {
                    "href": "/api/storage/volumes/73b293df-e9d7-46cc-a9ce-2df8e52ef864/files/dir1%2Fdir2?return_metadata=true"
                }
            },
        }
    ),
    TopMetricsDirectory(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/572361f3-e769-439d-9c04-2ba48a08ff43"
                    }
                },
                "uuid": "572361f3-e769-439d-9c04-2ba48a08ff43",
                "name": "vs1",
            },
            "volume": {"name": "vol1"},
            "iops": {"error": {"upper_bound": 1032, "lower_bound": 1022}, "read": 1022},
            "path": "/dir3/dir4",
            "_links": {
                "metadata": {
                    "href": "/api/storage/volumes/73b293df-e9d7-46cc-a9ce-2df8e52ef864/files/dir3%2Fdir4?return_metadata=true"
                }
            },
        }
    ),
    TopMetricsDirectory(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/572361f3-e769-439d-9c04-2ba48a08ff43"
                    }
                },
                "uuid": "572361f3-e769-439d-9c04-2ba48a08ff43",
                "name": "vs1",
            },
            "volume": {
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/73b293df-e9d7-46cc-a9ce-2df8e52ef864"
                    }
                },
                "uuid": "73b293df-e9d7-46cc-a9ce-2df8e52ef864",
                "name": "vol1",
            },
            "iops": {"error": {"upper_bound": 355, "lower_bound": 345}, "read": 345},
            "path": "/dir12",
            "_links": {
                "metadata": {
                    "href": "/api/storage/volumes/73b293df-e9d7-46cc-a9ce-2df8e52ef864/files/dir12?return_metadata=true"
                }
            },
        }
    ),
]

```
</div>
</div>

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


__all__ = ["TopMetricsDirectory", "TopMetricsDirectorySchema"]
__pdoc__ = {
    "TopMetricsDirectorySchema.resource": False,
    "TopMetricsDirectory.top_metrics_directory_show": False,
    "TopMetricsDirectory.top_metrics_directory_create": False,
    "TopMetricsDirectory.top_metrics_directory_modify": False,
    "TopMetricsDirectory.top_metrics_directory_delete": False,
}


class TopMetricsDirectorySchema(ResourceSchema):
    """The fields of the TopMetricsDirectory object"""

    links = fields.Nested("netapp_ontap.models.file_info_links.FileInfoLinksSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the top_metrics_directory. """

    iops = fields.Nested("netapp_ontap.models.top_metrics_directory_iops.TopMetricsDirectoryIopsSchema", data_key="iops", unknown=EXCLUDE)
    r""" The iops field of the top_metrics_directory. """

    path = fields.Str(
        data_key="path",
    )
    r""" Path of the directory.

Example: /dir_abc/dir_123/dir_20 """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the top_metrics_directory. """

    throughput = fields.Nested("netapp_ontap.models.top_metrics_directory_throughput.TopMetricsDirectoryThroughputSchema", data_key="throughput", unknown=EXCLUDE)
    r""" The throughput field of the top_metrics_directory. """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the top_metrics_directory. """

    @property
    def resource(self):
        return TopMetricsDirectory

    gettable_fields = [
        "links",
        "iops",
        "path",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "throughput",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,iops,path,svm.links,svm.name,svm.uuid,throughput,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "iops",
        "svm.name",
        "svm.uuid",
        "throughput",
        "volume.name",
        "volume.uuid",
    ]
    """iops,svm.name,svm.uuid,throughput,volume.name,volume.uuid,"""

    postable_fields = [
        "iops",
        "svm.name",
        "svm.uuid",
        "throughput",
        "volume.name",
        "volume.uuid",
    ]
    """iops,svm.name,svm.uuid,throughput,volume.name,volume.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in TopMetricsDirectory.get_collection(fields=field)]
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
            raise NetAppRestError("TopMetricsDirectory modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class TopMetricsDirectory(Resource):
    r""" Information about a directory's IO activity. """

    _schema = TopMetricsDirectorySchema
    _path = "/api/storage/volumes/{volume[uuid]}/top-metrics/directories"
    _keys = ["volume.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a list of directories with the most IO activity.
### Learn more
* [`DOC /storage/volumes/{volume.uuid}/top-metrics/directories`](#docs-storage-storage_volumes_{volume.uuid}_top-metrics_directories)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="top metrics directory show")
        def top_metrics_directory_show(
            volume_uuid,
            path: Choices.define(_get_field_list("path"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["path", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of TopMetricsDirectory resources

            Args:
                path: Path of the directory.
            """

            kwargs = {}
            if path is not None:
                kwargs["path"] = path
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return TopMetricsDirectory.get_collection(
                volume_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all TopMetricsDirectory resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a list of directories with the most IO activity.
### Learn more
* [`DOC /storage/volumes/{volume.uuid}/top-metrics/directories`](#docs-storage-storage_volumes_{volume.uuid}_top-metrics_directories)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)






