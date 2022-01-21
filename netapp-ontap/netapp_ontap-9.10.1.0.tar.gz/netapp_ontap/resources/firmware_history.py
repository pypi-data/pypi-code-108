r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Use this API to retrieve a history of firmware update requests. This API supports GET calls.
---
## Examples
### Retrieving history of firmware updates
The following example retrieves a history of firmware updates performed on the cluster.
Note that if the <i>fields=*</i> parameter is not specified, only the job ID and start time are returned.
Filters can be added on the fields to limit the results.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FirmwareHistory

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(FirmwareHistory.get_collection(fields="*")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    FirmwareHistory(
        {
            "update_status": [
                {
                    "worker": {
                        "error": {
                            "code": 2228327,
                            "message": "A firmware file already exists.",
                        },
                        "node": {
                            "uuid": "0530d6c1-8c6d-11e8-907f-00a0985a72ee",
                            "name": "node1",
                        },
                        "state": "failed",
                    }
                },
                {
                    "worker": {
                        "error": {"code": 0, "message": "Success"},
                        "node": {
                            "uuid": "0530d6c1-8c6d-11e8-907f-00a0985a72ef",
                            "name": "node2",
                        },
                        "state": "complete",
                    }
                },
            ],
            "start_time": "1970-01-01T00:02:03+00:00",
            "job": {"uuid": "adf700c2-b50e-11ea-a54f-005056bbec43"},
            "fw_file_name": "all_disk_fw.zip",
            "end_time": "1970-01-01T00:07:36+00:00",
            "fw_update_state": "starting_workers",
            "node": {"uuid": "0530d6c1-8c6d-11e8-907f-00a0985a72ee", "name": "node1"},
            "_links": {
                "self": {
                    "href": "/api/cluster/firmware/history/1970-01-01T00%3A02%3A03-00%3A00/adf700c2-b50e-11ea-a54f-005056bbec43"
                }
            },
        }
    ),
    FirmwareHistory(
        {
            "update_status": [
                {
                    "worker": {
                        "error": {
                            "code": 2228327,
                            "message": "A firmware file already exists.",
                        },
                        "node": {
                            "uuid": "0530d6c1-8c6d-11e8-907f-00a0985a72ee",
                            "name": "node1",
                        },
                        "state": "failed",
                    }
                },
                {
                    "worker": {
                        "error": {"code": 0, "message": "Success"},
                        "node": {
                            "uuid": "0530d6c1-8c6d-11e8-907f-00a0985a72ef",
                            "name": "node2",
                        },
                        "state": "complete",
                    }
                },
            ],
            "start_time": "1970-01-01T00:02:03+00:00",
            "job": {"uuid": "f84adabe-b50e-11ea-a54f-005056bbec43"},
            "fw_file_name": "all_shelf_fw.zip",
            "end_time": "1970-01-01T00:07:36+00:00",
            "fw_update_state": "completed",
            "node": {"uuid": "0530d6c1-8c6d-11e8-907f-00a0985a72ee", "name": "node1"},
            "_links": {
                "self": {
                    "href": "/api/cluster/firmware/history/1970-01-01T00%3A02%3A03-00%3A00/f84adabe-b50e-11ea-a54f-005056bbec43"
                }
            },
        }
    ),
]

```
</div>
</div>

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


__all__ = ["FirmwareHistory", "FirmwareHistorySchema"]
__pdoc__ = {
    "FirmwareHistorySchema.resource": False,
    "FirmwareHistory.firmware_history_show": False,
    "FirmwareHistory.firmware_history_create": False,
    "FirmwareHistory.firmware_history_modify": False,
    "FirmwareHistory.firmware_history_delete": False,
}


class FirmwareHistorySchema(ResourceSchema):
    """The fields of the FirmwareHistory object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the firmware_history. """

    end_time = ImpreciseDateTime(
        data_key="end_time",
    )
    r""" End time of this update request.

Example: 2019-02-02T19:00:00.000+0000 """

    fw_file_name = fields.Str(
        data_key="fw_file_name",
    )
    r""" Name of the firmware file.

Example: all_disk_fw.zip """

    fw_update_state = fields.Str(
        data_key="fw_update_state",
        validate=enum_validation(['downloading', 'moving_firmware', 'starting_workers', 'waiting_on_workers', 'completed', 'failed']),
    )
    r""" The fw_update_state field of the firmware_history.

Valid choices:

* downloading
* moving_firmware
* starting_workers
* waiting_on_workers
* completed
* failed """

    job = fields.Nested("netapp_ontap.models.job_link.JobLinkSchema", data_key="job", unknown=EXCLUDE)
    r""" The job field of the firmware_history. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the firmware_history. """

    start_time = ImpreciseDateTime(
        data_key="start_time",
    )
    r""" Start time of this update request.

Example: 2019-02-02T19:00:00.000+0000 """

    update_status = fields.List(fields.Nested("netapp_ontap.models.firmware_history_update_state.FirmwareHistoryUpdateStateSchema", unknown=EXCLUDE), data_key="update_status")
    r""" The update_status field of the firmware_history. """

    @property
    def resource(self):
        return FirmwareHistory

    gettable_fields = [
        "links",
        "end_time",
        "fw_file_name",
        "fw_update_state",
        "job",
        "node.links",
        "node.name",
        "node.uuid",
        "start_time",
        "update_status",
    ]
    """links,end_time,fw_file_name,fw_update_state,job,node.links,node.name,node.uuid,start_time,update_status,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FirmwareHistory.get_collection(fields=field)]
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
            raise NetAppRestError("FirmwareHistory modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FirmwareHistory(Resource):
    """Allows interaction with FirmwareHistory objects on the host"""

    _schema = FirmwareHistorySchema
    _path = "/api/cluster/firmware/history"

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the history details for firmware update requests.
### Learn more
* [`DOC /cluster/firmware/history`](#docs-cluster-cluster_firmware_history)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="firmware history show")
        def firmware_history_show(
            fields: List[Choices.define(["end_time", "fw_file_name", "fw_update_state", "start_time", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of FirmwareHistory resources

            Args:
                end_time: End time of this update request.
                fw_file_name: Name of the firmware file.
                fw_update_state: 
                start_time: Start time of this update request.
            """

            kwargs = {}
            if end_time is not None:
                kwargs["end_time"] = end_time
            if fw_file_name is not None:
                kwargs["fw_file_name"] = fw_file_name
            if fw_update_state is not None:
                kwargs["fw_update_state"] = fw_update_state
            if start_time is not None:
                kwargs["start_time"] = start_time
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return FirmwareHistory.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all FirmwareHistory resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the history details for firmware update requests.
### Learn more
* [`DOC /cluster/firmware/history`](#docs-cluster-cluster_firmware_history)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)






