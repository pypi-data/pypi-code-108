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


__all__ = ["NvmeSubsystemHost", "NvmeSubsystemHostSchema"]
__pdoc__ = {
    "NvmeSubsystemHostSchema.resource": False,
    "NvmeSubsystemHost.nvme_subsystem_host_show": False,
    "NvmeSubsystemHost.nvme_subsystem_host_create": False,
    "NvmeSubsystemHost.nvme_subsystem_host_modify": False,
    "NvmeSubsystemHost.nvme_subsystem_host_delete": False,
}


class NvmeSubsystemHostSchema(ResourceSchema):
    """The fields of the NvmeSubsystemHost object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the nvme_subsystem_host. """

    io_queue = fields.Nested("netapp_ontap.models.nvme_subsystem_host_io_queue.NvmeSubsystemHostIoQueueSchema", data_key="io_queue", unknown=EXCLUDE)
    r""" The io_queue field of the nvme_subsystem_host. """

    nqn = fields.Str(
        data_key="nqn",
    )
    r""" The NVMe qualified name (NQN) used to identify the NVMe storage target. Not allowed in POST when the `records` property is used.


Example: nqn.1992-01.example.com:string """

    records = fields.List(fields.Nested("netapp_ontap.models.nvme_subsystem_host_no_records.NvmeSubsystemHostNoRecordsSchema", unknown=EXCLUDE), data_key="records")
    r""" An array of NVMe hosts specified to add multiple NVMe hosts to an NVMe subsystem in a single API call. Valid in POST only. """

    subsystem = fields.Nested("netapp_ontap.models.nvme_subsystem_host_subsystem.NvmeSubsystemHostSubsystemSchema", data_key="subsystem", unknown=EXCLUDE)
    r""" The subsystem field of the nvme_subsystem_host. """

    @property
    def resource(self):
        return NvmeSubsystemHost

    gettable_fields = [
        "links",
        "io_queue",
        "nqn",
        "subsystem",
    ]
    """links,io_queue,nqn,subsystem,"""

    patchable_fields = [
        "io_queue",
        "subsystem",
    ]
    """io_queue,subsystem,"""

    postable_fields = [
        "io_queue",
        "nqn",
        "records",
        "subsystem",
    ]
    """io_queue,nqn,records,subsystem,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NvmeSubsystemHost.get_collection(fields=field)]
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
            raise NetAppRestError("NvmeSubsystemHost modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NvmeSubsystemHost(Resource):
    r""" The NVMe host provisioned to access NVMe namespaces mapped to a subsystem. """

    _schema = NvmeSubsystemHostSchema
    _path = "/api/protocols/nvme/subsystems/{subsystem[uuid]}/hosts"
    _keys = ["subsystem.uuid", "nqn"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the NVMe subsystem hosts of an NVMe subsystem.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `subsystem_maps.*`
### Related ONTAP commands
* `vserver nvme subsystem map show`
* `vserver nvme subsystem show`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme subsystem host show")
        def nvme_subsystem_host_show(
            subsystem_uuid,
            nqn: Choices.define(_get_field_list("nqn"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["nqn", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of NvmeSubsystemHost resources

            Args:
                nqn: The NVMe qualified name (NQN) used to identify the NVMe storage target. Not allowed in POST when the `records` property is used. 
            """

            kwargs = {}
            if nqn is not None:
                kwargs["nqn"] = nqn
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return NvmeSubsystemHost.get_collection(
                subsystem_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NvmeSubsystemHost resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["NvmeSubsystemHost"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["NvmeSubsystemHost"], NetAppResponse]:
        r"""Adds NVMe subsystem host(s) to an NVMe subsystem.
### Required properties
* `nqn` or `records.nqn` - NVMe host(s) NQN(s) to add to the NVMe subsystem.
### Related ONTAP commands
* `vserver nvme subsystem host add`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
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
        records: Iterable["NvmeSubsystemHost"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an NVMe subsystem host from an NVMe subsystem.
### Related ONTAP commands
* `vserver nvme subsystem host remove`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the NVMe subsystem hosts of an NVMe subsystem.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `subsystem_maps.*`
### Related ONTAP commands
* `vserver nvme subsystem map show`
* `vserver nvme subsystem show`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an NVMe subsystem host of an NVMe subsystem.
### Related ONTAP commands
* `vserver nvme subsystem host show`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
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
        r"""Adds NVMe subsystem host(s) to an NVMe subsystem.
### Required properties
* `nqn` or `records.nqn` - NVMe host(s) NQN(s) to add to the NVMe subsystem.
### Related ONTAP commands
* `vserver nvme subsystem host add`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme subsystem host create")
        async def nvme_subsystem_host_create(
            subsystem_uuid,
            links: dict = None,
            io_queue: dict = None,
            nqn: str = None,
            records: dict = None,
            subsystem: dict = None,
        ) -> ResourceTable:
            """Create an instance of a NvmeSubsystemHost resource

            Args:
                links: 
                io_queue: 
                nqn: The NVMe qualified name (NQN) used to identify the NVMe storage target. Not allowed in POST when the `records` property is used. 
                records: An array of NVMe hosts specified to add multiple NVMe hosts to an NVMe subsystem in a single API call. Valid in POST only. 
                subsystem: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if io_queue is not None:
                kwargs["io_queue"] = io_queue
            if nqn is not None:
                kwargs["nqn"] = nqn
            if records is not None:
                kwargs["records"] = records
            if subsystem is not None:
                kwargs["subsystem"] = subsystem

            resource = NvmeSubsystemHost(
                subsystem_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create NvmeSubsystemHost: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an NVMe subsystem host from an NVMe subsystem.
### Related ONTAP commands
* `vserver nvme subsystem host remove`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nvme subsystem host delete")
        async def nvme_subsystem_host_delete(
            subsystem_uuid,
            nqn: str = None,
        ) -> None:
            """Delete an instance of a NvmeSubsystemHost resource

            Args:
                nqn: The NVMe qualified name (NQN) used to identify the NVMe storage target. Not allowed in POST when the `records` property is used. 
            """

            kwargs = {}
            if nqn is not None:
                kwargs["nqn"] = nqn

            if hasattr(NvmeSubsystemHost, "find"):
                resource = NvmeSubsystemHost.find(
                    subsystem_uuid,
                    **kwargs
                )
            else:
                resource = NvmeSubsystemHost(subsystem_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete NvmeSubsystemHost: %s" % err)


