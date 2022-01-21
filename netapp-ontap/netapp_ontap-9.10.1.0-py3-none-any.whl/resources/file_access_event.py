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


__all__ = ["FileAccessEvent", "FileAccessEventSchema"]
__pdoc__ = {
    "FileAccessEventSchema.resource": False,
    "FileAccessEvent.file_access_event_show": False,
    "FileAccessEvent.file_access_event_create": False,
    "FileAccessEvent.file_access_event_modify": False,
    "FileAccessEvent.file_access_event_delete": False,
}


class FileAccessEventSchema(ResourceSchema):
    """The fields of the FileAccessEvent object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the file_access_event. """

    create_time = ImpreciseDateTime(
        data_key="create_time",
    )
    r""" Specifies the time at which the trace event entry was generated.

Example: 2018-06-04T19:00:00.000+0000 """

    filter = fields.Nested("netapp_ontap.resources.file_access_filter.FileAccessFilterSchema", data_key="filter", unknown=EXCLUDE)
    r""" The filter field of the file_access_event. """

    index = Size(
        data_key="index",
    )
    r""" Specifies the sequence number of the security trace event.

Example: 1 """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the file_access_event. """

    reason = fields.Nested("netapp_ontap.models.file_access_event_reason.FileAccessEventReasonSchema", data_key="reason", unknown=EXCLUDE)
    r""" The reason field of the file_access_event. """

    session_id = Size(
        data_key="session_id",
    )
    r""" Specifies the CIFS session ID for the file access trace event, this is generated only for CIFS file accesses.

Example: 2628976282477527056 """

    share = fields.Nested("netapp_ontap.resources.cifs_share.CifsShareSchema", data_key="share", unknown=EXCLUDE)
    r""" The share field of the file_access_event. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the file_access_event. """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the file_access_event. """

    @property
    def resource(self):
        return FileAccessEvent

    gettable_fields = [
        "links",
        "create_time",
        "filter",
        "index",
        "node.links",
        "node.name",
        "node.uuid",
        "reason",
        "session_id",
        "share.links",
        "share.name",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,create_time,filter,index,node.links,node.name,node.uuid,reason,session_id,share.links,share.name,svm.links,svm.name,svm.uuid,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FileAccessEvent.get_collection(fields=field)]
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
            raise NetAppRestError("FileAccessEvent modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FileAccessEvent(Resource):
    r""" ONTAP generates the list of file access tracing records stored on the cluster. These records are generated in response to security trace filters applied. The list of trace events recorded depends on the parameters configured for the filter. """

    _schema = FileAccessEventSchema
    _path = "/api/protocols/file-access-tracing/events"
    _keys = ["node.uuid", "svm.uuid", "index"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the trace results for access allowed or denied events.
### Related ONTAP commands
* `vserver security trace trace-result show`
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file access event show")
        def file_access_event_show(
            fields: List[Choices.define(["create_time", "index", "session_id", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of FileAccessEvent resources

            Args:
                create_time: Specifies the time at which the trace event entry was generated.
                index: Specifies the sequence number of the security trace event.
                session_id: Specifies the CIFS session ID for the file access trace event, this is generated only for CIFS file accesses.
            """

            kwargs = {}
            if create_time is not None:
                kwargs["create_time"] = create_time
            if index is not None:
                kwargs["index"] = index
            if session_id is not None:
                kwargs["session_id"] = session_id
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return FileAccessEvent.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all FileAccessEvent resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)



    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["FileAccessEvent"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes trace results.
### Related ONTAP commands
* `vserver security trace result delete`
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the trace results for access allowed or denied events.
### Related ONTAP commands
* `vserver security trace trace-result show`
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves trace results for the specified sequence number.
### Related ONTAP commands
* `vserver security trace trace-result show`
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)



    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes trace results.
### Related ONTAP commands
* `vserver security trace result delete`
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file access event delete")
        async def file_access_event_delete(
        ) -> None:
            """Delete an instance of a FileAccessEvent resource

            Args:
                create_time: Specifies the time at which the trace event entry was generated.
                index: Specifies the sequence number of the security trace event.
                session_id: Specifies the CIFS session ID for the file access trace event, this is generated only for CIFS file accesses.
            """

            kwargs = {}
            if create_time is not None:
                kwargs["create_time"] = create_time
            if index is not None:
                kwargs["index"] = index
            if session_id is not None:
                kwargs["session_id"] = session_id

            if hasattr(FileAccessEvent, "find"):
                resource = FileAccessEvent.find(
                    **kwargs
                )
            else:
                resource = FileAccessEvent()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete FileAccessEvent: %s" % err)


