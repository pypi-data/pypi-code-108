r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
You can use this API to retrieve a list of users with the most IO activity for a specified volume. Use the `top_metric` parameter to specify which type of IO activity to filter for. This API is used to provide insight into IO activity and supports ordering by IO activity types, namely `iops` or `throughput` metrics. This API also supports only returning one IO activity type per request.
## Retrieve a list of the users with the most IO activity
For a report on the users with the most IO activity returned in descending order, specify the IO activity type you want to filter for by passing the `iops` or `throughput` property into the top_metric parameter. If the IO activity type is not specified, by default the API returns a list of the users with the greatest number of the average read operations per second. The maximum number of users returned by the API for an IO activity type is 25.

* GET   /api/storage/volumes/{volume.uuid}/top-metrics/users
## Examples
### Retrieving a list of the users with the greatest average number of read bytes received per second:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import TopMetricsUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            TopMetricsUser.get_collection("{volume.uuid}", top_metric="throughput.read")
        )
    )

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    TopMetricsUser(
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
            "throughput": {
                "error": {"upper_bound": 1502, "lower_bound": 1495},
                "read": 1495,
            },
            "user_name": "John",
            "user_id": "S-1-5-21-256008430-3394229847-3930036330-1001",
        }
    ),
    TopMetricsUser(
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
            "throughput": {
                "error": {"upper_bound": 1025, "lower_bound": 1022},
                "read": 1022,
            },
            "user_name": "Ryan",
            "user_id": "1988",
        }
    ),
    TopMetricsUser(
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
            "throughput": {
                "error": {"upper_bound": 348, "lower_bound": 345},
                "read": 345,
            },
            "user_name": "Julie",
            "user_id": "S-1-5-21-256008430-3394229847-3930036330-1003",
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


__all__ = ["TopMetricsUser", "TopMetricsUserSchema"]
__pdoc__ = {
    "TopMetricsUserSchema.resource": False,
    "TopMetricsUser.top_metrics_user_show": False,
    "TopMetricsUser.top_metrics_user_create": False,
    "TopMetricsUser.top_metrics_user_modify": False,
    "TopMetricsUser.top_metrics_user_delete": False,
}


class TopMetricsUserSchema(ResourceSchema):
    """The fields of the TopMetricsUser object"""

    iops = fields.Nested("netapp_ontap.models.top_metrics_user_iops.TopMetricsUserIopsSchema", data_key="iops", unknown=EXCLUDE)
    r""" The iops field of the top_metrics_user. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the top_metrics_user. """

    throughput = fields.Nested("netapp_ontap.models.top_metrics_user_throughput.TopMetricsUserThroughputSchema", data_key="throughput", unknown=EXCLUDE)
    r""" The throughput field of the top_metrics_user. """

    user_id = fields.Str(
        data_key="user_id",
    )
    r""" User ID of the user.

Example: S-1-5-21-256008430-3394229847-3930036330-1001 """

    user_name = fields.Str(
        data_key="user_name",
    )
    r""" Name of the user.

Example: James """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the top_metrics_user. """

    @property
    def resource(self):
        return TopMetricsUser

    gettable_fields = [
        "iops",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "throughput",
        "user_id",
        "user_name",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """iops,svm.links,svm.name,svm.uuid,throughput,user_id,user_name,volume.links,volume.name,volume.uuid,"""

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
        return [getattr(r, field) for r in TopMetricsUser.get_collection(fields=field)]
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
            raise NetAppRestError("TopMetricsUser modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class TopMetricsUser(Resource):
    r""" Information about a user's IO activity. """

    _schema = TopMetricsUserSchema
    _path = "/api/storage/volumes/{volume[uuid]}/top-metrics/users"
    _keys = ["volume.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a list of users with the most IO activity.
### Learn more
* [`DOC /storage/volumes/{volume.uuid}/top-metrics/users`](#docs-storage-storage_volumes_{volume.uuid}_top-metrics_users)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="top metrics user show")
        def top_metrics_user_show(
            volume_uuid,
            user_id: Choices.define(_get_field_list("user_id"), cache_choices=True, inexact=True)=None,
            user_name: Choices.define(_get_field_list("user_name"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["user_id", "user_name", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of TopMetricsUser resources

            Args:
                user_id: User ID of the user.
                user_name: Name of the user.
            """

            kwargs = {}
            if user_id is not None:
                kwargs["user_id"] = user_id
            if user_name is not None:
                kwargs["user_name"] = user_name
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return TopMetricsUser.get_collection(
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
        """Returns a count of all TopMetricsUser resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a list of users with the most IO activity.
### Learn more
* [`DOC /storage/volumes/{volume.uuid}/top-metrics/users`](#docs-storage-storage_volumes_{volume.uuid}_top-metrics_users)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)






