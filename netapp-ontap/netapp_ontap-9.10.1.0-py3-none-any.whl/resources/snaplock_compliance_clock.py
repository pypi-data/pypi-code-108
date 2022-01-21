r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

This API manages the ComplianceClock of the system. ComplianceClock determines the expiry time of the SnapLock objects in the system. The user can initialize the ComplianceClock once and when it is set, it cannot be changed by the user.
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


__all__ = ["SnaplockComplianceClock", "SnaplockComplianceClockSchema"]
__pdoc__ = {
    "SnaplockComplianceClockSchema.resource": False,
    "SnaplockComplianceClock.snaplock_compliance_clock_show": False,
    "SnaplockComplianceClock.snaplock_compliance_clock_create": False,
    "SnaplockComplianceClock.snaplock_compliance_clock_modify": False,
    "SnaplockComplianceClock.snaplock_compliance_clock_delete": False,
}


class SnaplockComplianceClockSchema(ResourceSchema):
    """The fields of the SnaplockComplianceClock object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the snaplock_compliance_clock. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the snaplock_compliance_clock. """

    time = ImpreciseDateTime(
        data_key="time",
    )
    r""" Compliance clock time

Example: 2018-06-04T19:00:00.000+0000 """

    @property
    def resource(self):
        return SnaplockComplianceClock

    gettable_fields = [
        "links",
        "node.links",
        "node.name",
        "node.uuid",
        "time",
    ]
    """links,node.links,node.name,node.uuid,time,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "node.name",
        "node.uuid",
    ]
    """node.name,node.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SnaplockComplianceClock.get_collection(fields=field)]
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
            raise NetAppRestError("SnaplockComplianceClock modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SnaplockComplianceClock(Resource):
    """Allows interaction with SnaplockComplianceClock objects on the host"""

    _schema = SnaplockComplianceClockSchema
    _path = "/api/storage/snaplock/compliance-clocks"
    _keys = ["node.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the SnapLock ComplianceClock for all of the nodes in the cluster.
### Related ONTAP commands
* `snaplock compliance-clock show`
### Learn more
* [`DOC /storage/snaplock/compliance-clocks`](#docs-snaplock-storage_snaplock_compliance-clocks)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock compliance clock show")
        def snaplock_compliance_clock_show(
            fields: List[Choices.define(["time", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SnaplockComplianceClock resources

            Args:
                time: Compliance clock time
            """

            kwargs = {}
            if time is not None:
                kwargs["time"] = time
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SnaplockComplianceClock.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SnaplockComplianceClock resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["SnaplockComplianceClock"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["SnaplockComplianceClock"], NetAppResponse]:
        r"""Initializes the SnapLock ComplianceClock.
### Required properties
* `node.name` or `node.uuid` - Name or UUID of the node.
### Related ONTAP commands
* `snaplock compliance-clock initialize`
### Learn more
* [`DOC /storage/snaplock/compliance-clocks`](#docs-snaplock-storage_snaplock_compliance-clocks)
"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)


    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the SnapLock ComplianceClock for all of the nodes in the cluster.
### Related ONTAP commands
* `snaplock compliance-clock show`
### Learn more
* [`DOC /storage/snaplock/compliance-clocks`](#docs-snaplock-storage_snaplock_compliance-clocks)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the SnapLock ComplianceClock for a specific node.
### Related ONTAP commands
* `snaplock compliance-clock show`
### Learn more
* [`DOC /storage/snaplock/compliance-clocks`](#docs-snaplock-storage_snaplock_compliance-clocks)
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
        r"""Initializes the SnapLock ComplianceClock.
### Required properties
* `node.name` or `node.uuid` - Name or UUID of the node.
### Related ONTAP commands
* `snaplock compliance-clock initialize`
### Learn more
* [`DOC /storage/snaplock/compliance-clocks`](#docs-snaplock-storage_snaplock_compliance-clocks)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock compliance clock create")
        async def snaplock_compliance_clock_create(
        ) -> ResourceTable:
            """Create an instance of a SnaplockComplianceClock resource

            Args:
                links: 
                node: 
                time: Compliance clock time
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if node is not None:
                kwargs["node"] = node
            if time is not None:
                kwargs["time"] = time

            resource = SnaplockComplianceClock(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SnaplockComplianceClock: %s" % err)
            return [resource]




