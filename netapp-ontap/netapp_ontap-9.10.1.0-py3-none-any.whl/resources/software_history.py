r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


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


__all__ = ["SoftwareHistory", "SoftwareHistorySchema"]
__pdoc__ = {
    "SoftwareHistorySchema.resource": False,
    "SoftwareHistory.software_history_show": False,
    "SoftwareHistory.software_history_create": False,
    "SoftwareHistory.software_history_modify": False,
    "SoftwareHistory.software_history_delete": False,
}


class SoftwareHistorySchema(ResourceSchema):
    """The fields of the SoftwareHistory object"""

    end_time = ImpreciseDateTime(
        data_key="end_time",
    )
    r""" Completion time of this installation request.

Example: 2019-02-02T20:00:00.000+0000 """

    from_version = fields.Str(
        data_key="from_version",
    )
    r""" Previous version of node

Example: ONTAP_X1 """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the software_history. """

    start_time = ImpreciseDateTime(
        data_key="start_time",
    )
    r""" Start time of this installation request.

Example: 2019-02-02T19:00:00.000+0000 """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['successful', 'canceled']),
    )
    r""" Status of this installation request.

Valid choices:

* successful
* canceled """

    to_version = fields.Str(
        data_key="to_version",
    )
    r""" Updated version of node

Example: ONTAP_X2 """

    @property
    def resource(self):
        return SoftwareHistory

    gettable_fields = [
        "end_time",
        "from_version",
        "node.links",
        "node.name",
        "node.uuid",
        "start_time",
        "state",
        "to_version",
    ]
    """end_time,from_version,node.links,node.name,node.uuid,start_time,state,to_version,"""

    patchable_fields = [
        "node.name",
        "node.uuid",
    ]
    """node.name,node.uuid,"""

    postable_fields = [
        "node.name",
        "node.uuid",
    ]
    """node.name,node.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SoftwareHistory.get_collection(fields=field)]
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
            raise NetAppRestError("SoftwareHistory modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SoftwareHistory(Resource):
    """Allows interaction with SoftwareHistory objects on the host"""

    _schema = SoftwareHistorySchema
    _path = "/api/cluster/software/history"

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the history details for software installation requests.
### Related ONTAP commands
* `cluster image show-update-history`
### Learn more
* [`DOC /cluster/software`](#docs-cluster-cluster_software)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="software history show")
        def software_history_show(
            fields: List[Choices.define(["end_time", "from_version", "start_time", "state", "to_version", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SoftwareHistory resources

            Args:
                end_time: Completion time of this installation request.
                from_version: Previous version of node
                start_time: Start time of this installation request.
                state: Status of this installation request.
                to_version: Updated version of node
            """

            kwargs = {}
            if end_time is not None:
                kwargs["end_time"] = end_time
            if from_version is not None:
                kwargs["from_version"] = from_version
            if start_time is not None:
                kwargs["start_time"] = start_time
            if state is not None:
                kwargs["state"] = state
            if to_version is not None:
                kwargs["to_version"] = to_version
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SoftwareHistory.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SoftwareHistory resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the history details for software installation requests.
### Related ONTAP commands
* `cluster image show-update-history`
### Learn more
* [`DOC /cluster/software`](#docs-cluster-cluster_software)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)






