r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
You can use this API to retrieve a list of files with the most IO activity for a specified volume. Use the `top_metric` parameter to specify which type of IO activity to filter for. This API is used to provide insight into IO activity and supports ordering by IO activity types, namely `iops` or `throughput` metrics. This API also supports only returning one IO activity type per request.
## Retrieve a list of the files with the most IO activity
For a report on the files with the most IO activity returned in descending order, specify the IO activity type you want to filter for by passing the `iops` or `throughput` property into the top_metric parameter. If the IO activity type is not specified, by default the API returns a list of the files with the greatest number of the average read operations per second. The maximum number of files returned by the API for an IO activity type is 25.

* GET   /api/storage/volumes/{volume.uuid}/top-metrics/files
## Examples
### Retrieving a list of the files with the greatest average number of write bytes received per second:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import TopMetricsFile

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            TopMetricsFile.get_collection(
                "{volume.uuid}", top_metric="throughput.write"
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
    TopMetricsFile(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/0ba74c3e-d5ca-11eb-8fbb-005056ac0f77"
                    }
                },
                "uuid": "0ba74c3e-d5ca-11eb-8fbb-005056ac0f77",
                "name": "vs0",
            },
            "volume": {"name": "fv"},
            "throughput": {
                "error": {"upper_bound": 29, "lower_bound": 24},
                "write": 24,
            },
            "path": "/d5/f5",
            "_links": {
                "metadata": {
                    "href": "/api/storage/volumes/4ec6d1ea-d5da-11eb-a25f-005056ac0f77/files/d5%2Ff5?return_metadata=true"
                }
            },
        }
    ),
    TopMetricsFile(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/0ba74c3e-d5ca-11eb-8fbb-005056ac0f77"
                    }
                },
                "uuid": "0ba74c3e-d5ca-11eb-8fbb-005056ac0f77",
                "name": "vs0",
            },
            "volume": {"name": "fv"},
            "throughput": {
                "error": {"upper_bound": 22, "lower_bound": 12},
                "write": 12,
            },
            "path": "/d6/f6",
            "_links": {
                "metadata": {
                    "href": "/api/storage/volumes/4ec6d1ea-d5da-11eb-a25f-005056ac0f77/files/d6%2Ff6?return_metadata=true"
                }
            },
        }
    ),
    TopMetricsFile(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/0ba74c3e-d5ca-11eb-8fbb-005056ac0f77"
                    }
                },
                "uuid": "0ba74c3e-d5ca-11eb-8fbb-005056ac0f77",
                "name": "vs0",
            },
            "volume": {"name": "fv"},
            "throughput": {"error": {"upper_bound": 10, "lower_bound": 8}, "write": 8},
            "path": "/d3/f3",
            "_links": {
                "metadata": {
                    "href": "/api/storage/volumes/4ec6d1ea-d5da-11eb-a25f-005056ac0f77/files/d3%2Ff3?return_metadata=true"
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


__all__ = ["TopMetricsFile", "TopMetricsFileSchema"]
__pdoc__ = {
    "TopMetricsFileSchema.resource": False,
    "TopMetricsFile.top_metrics_file_show": False,
    "TopMetricsFile.top_metrics_file_create": False,
    "TopMetricsFile.top_metrics_file_modify": False,
    "TopMetricsFile.top_metrics_file_delete": False,
}


class TopMetricsFileSchema(ResourceSchema):
    """The fields of the TopMetricsFile object"""

    links = fields.Nested("netapp_ontap.models.file_info_links.FileInfoLinksSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the top_metrics_file. """

    iops = fields.Nested("netapp_ontap.models.top_metrics_file_iops.TopMetricsFileIopsSchema", data_key="iops", unknown=EXCLUDE)
    r""" The iops field of the top_metrics_file. """

    path = fields.Str(
        data_key="path",
    )
    r""" Path of the file.

Example: /dir_abc/dir_123/file_1 """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the top_metrics_file. """

    throughput = fields.Nested("netapp_ontap.models.top_metrics_file_throughput.TopMetricsFileThroughputSchema", data_key="throughput", unknown=EXCLUDE)
    r""" The throughput field of the top_metrics_file. """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the top_metrics_file. """

    @property
    def resource(self):
        return TopMetricsFile

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
        return [getattr(r, field) for r in TopMetricsFile.get_collection(fields=field)]
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
            raise NetAppRestError("TopMetricsFile modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class TopMetricsFile(Resource):
    r""" Information about a file's IO activity. """

    _schema = TopMetricsFileSchema
    _path = "/api/storage/volumes/{volume[uuid]}/top-metrics/files"
    _keys = ["volume.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a list of files with the most IO activity.
### Learn more
* [`DOC /storage/volumes/{volume.uuid}/top-metrics/files`](#docs-storage-storage_volumes_{volume.uuid}_top-metrics_files)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="top metrics file show")
        def top_metrics_file_show(
            volume_uuid,
            path: Choices.define(_get_field_list("path"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["path", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of TopMetricsFile resources

            Args:
                path: Path of the file.
            """

            kwargs = {}
            if path is not None:
                kwargs["path"] = path
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return TopMetricsFile.get_collection(
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
        """Returns a count of all TopMetricsFile resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a list of files with the most IO activity.
### Learn more
* [`DOC /storage/volumes/{volume.uuid}/top-metrics/files`](#docs-storage-storage_volumes_{volume.uuid}_top-metrics_files)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)






