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


__all__ = ["FileAccessFilter", "FileAccessFilterSchema"]
__pdoc__ = {
    "FileAccessFilterSchema.resource": False,
    "FileAccessFilter.file_access_filter_show": False,
    "FileAccessFilter.file_access_filter_create": False,
    "FileAccessFilter.file_access_filter_modify": False,
    "FileAccessFilter.file_access_filter_delete": False,
}


class FileAccessFilterSchema(ResourceSchema):
    """The fields of the FileAccessFilter object"""

    client_ip = fields.Str(
        data_key="client_ip",
    )
    r""" Specifies the IP address from which the client accesses the file or directory.

Example: 10.140.68.143 """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Specifies whether to enable or disable the filter. Filters are enabled by default and are deleted after 60 mins. """

    index = Size(
        data_key="index",
    )
    r""" Position of the file access tracing filter.

Example: 1 """

    path = fields.Str(
        data_key="path",
    )
    r""" Specifies the path for which permission tracing can be applied. The value can be complete path from root of CIFS share or root of volume for NFS.

Example: /dir1/dir2 """

    protocol = fields.Str(
        data_key="protocol",
        validate=enum_validation(['cifs', 'nfs']),
    )
    r""" Specifies the protocol for which permission trace is required.

Valid choices:

* cifs
* nfs """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the file_access_filter. """

    trace_allowed_ops = fields.Boolean(
        data_key="trace_allowed_ops",
    )
    r""" Specifies if the filter can trace file access denied and allowed events. The value of trace-allow is false by default, and it traces access denied events. The value is set to true for tracing access allowed events. """

    unix_user = fields.Str(
        data_key="unix_user",
    )
    r""" Specifies the UNIX username whose access requests you want to trace. The filter would match only if the request is received with this user.

Example: root """

    windows_user = fields.Str(
        data_key="windows_user",
    )
    r""" Specifies the Windows username whose access requests you want to trace. The filter would match only if the request is received with this user.

Example: cifs1/administrator """

    @property
    def resource(self):
        return FileAccessFilter

    gettable_fields = [
        "client_ip",
        "enabled",
        "index",
        "path",
        "protocol",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "trace_allowed_ops",
        "unix_user",
        "windows_user",
    ]
    """client_ip,enabled,index,path,protocol,svm.links,svm.name,svm.uuid,trace_allowed_ops,unix_user,windows_user,"""

    patchable_fields = [
        "client_ip",
        "enabled",
        "path",
        "protocol",
        "svm.name",
        "svm.uuid",
        "trace_allowed_ops",
        "unix_user",
        "windows_user",
    ]
    """client_ip,enabled,path,protocol,svm.name,svm.uuid,trace_allowed_ops,unix_user,windows_user,"""

    postable_fields = [
        "client_ip",
        "enabled",
        "path",
        "protocol",
        "svm.name",
        "svm.uuid",
        "trace_allowed_ops",
        "unix_user",
        "windows_user",
    ]
    """client_ip,enabled,path,protocol,svm.name,svm.uuid,trace_allowed_ops,unix_user,windows_user,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FileAccessFilter.get_collection(fields=field)]
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
            raise NetAppRestError("FileAccessFilter modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FileAccessFilter(Resource):
    r""" ONTAP allows creation of filters for file access tracing for both CIFS and NFS. These filters have protocols, path, username  and client IP based on which file access operations are logged. """

    _schema = FileAccessFilterSchema
    _path = "/api/protocols/file-access-tracing/filters"
    _keys = ["svm.uuid", "index"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves information about security trace filter entries.
### Related ONTAP commands
* `vserver security trace filter show`
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file access filter show")
        def file_access_filter_show(
            fields: List[Choices.define(["client_ip", "enabled", "index", "path", "protocol", "trace_allowed_ops", "unix_user", "windows_user", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of FileAccessFilter resources

            Args:
                client_ip: Specifies the IP address from which the client accesses the file or directory.
                enabled: Specifies whether to enable or disable the filter. Filters are enabled by default and are deleted after 60 mins.
                index: Position of the file access tracing filter.
                path: Specifies the path for which permission tracing can be applied. The value can be complete path from root of CIFS share or root of volume for NFS.
                protocol: Specifies the protocol for which permission trace is required.
                trace_allowed_ops: Specifies if the filter can trace file access denied and allowed events. The value of trace-allow is false by default, and it traces access denied events. The value is set to true for tracing access allowed events.
                unix_user: Specifies the UNIX username whose access requests you want to trace. The filter would match only if the request is received with this user.
                windows_user: Specifies the Windows username whose access requests you want to trace. The filter would match only if the request is received with this user.
            """

            kwargs = {}
            if client_ip is not None:
                kwargs["client_ip"] = client_ip
            if enabled is not None:
                kwargs["enabled"] = enabled
            if index is not None:
                kwargs["index"] = index
            if path is not None:
                kwargs["path"] = path
            if protocol is not None:
                kwargs["protocol"] = protocol
            if trace_allowed_ops is not None:
                kwargs["trace_allowed_ops"] = trace_allowed_ops
            if unix_user is not None:
                kwargs["unix_user"] = unix_user
            if windows_user is not None:
                kwargs["windows_user"] = windows_user
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return FileAccessFilter.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all FileAccessFilter resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["FileAccessFilter"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates security trace filter entries.
### Related ONTAP commands
* `vserver security trace filter modify`
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["FileAccessFilter"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["FileAccessFilter"], NetAppResponse]:
        r"""Creates security trace filter entries.
### Related ONTAP commands
* `vserver security trace filter create`
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
        records: Iterable["FileAccessFilter"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes security trace filters.
### Related ONTAP commands
* `vserver security trace filter delete`
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves information about security trace filter entries.
### Related ONTAP commands
* `vserver security trace filter show`
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves information about security trace filter entries.
### Related ONTAP commands
* `vserver security trace filter show`
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
        r"""Creates security trace filter entries.
### Related ONTAP commands
* `vserver security trace filter create`
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file access filter create")
        async def file_access_filter_create(
        ) -> ResourceTable:
            """Create an instance of a FileAccessFilter resource

            Args:
                client_ip: Specifies the IP address from which the client accesses the file or directory.
                enabled: Specifies whether to enable or disable the filter. Filters are enabled by default and are deleted after 60 mins.
                index: Position of the file access tracing filter.
                path: Specifies the path for which permission tracing can be applied. The value can be complete path from root of CIFS share or root of volume for NFS.
                protocol: Specifies the protocol for which permission trace is required.
                svm: 
                trace_allowed_ops: Specifies if the filter can trace file access denied and allowed events. The value of trace-allow is false by default, and it traces access denied events. The value is set to true for tracing access allowed events.
                unix_user: Specifies the UNIX username whose access requests you want to trace. The filter would match only if the request is received with this user.
                windows_user: Specifies the Windows username whose access requests you want to trace. The filter would match only if the request is received with this user.
            """

            kwargs = {}
            if client_ip is not None:
                kwargs["client_ip"] = client_ip
            if enabled is not None:
                kwargs["enabled"] = enabled
            if index is not None:
                kwargs["index"] = index
            if path is not None:
                kwargs["path"] = path
            if protocol is not None:
                kwargs["protocol"] = protocol
            if svm is not None:
                kwargs["svm"] = svm
            if trace_allowed_ops is not None:
                kwargs["trace_allowed_ops"] = trace_allowed_ops
            if unix_user is not None:
                kwargs["unix_user"] = unix_user
            if windows_user is not None:
                kwargs["windows_user"] = windows_user

            resource = FileAccessFilter(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create FileAccessFilter: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates security trace filter entries.
### Related ONTAP commands
* `vserver security trace filter modify`
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file access filter modify")
        async def file_access_filter_modify(
        ) -> ResourceTable:
            """Modify an instance of a FileAccessFilter resource

            Args:
                client_ip: Specifies the IP address from which the client accesses the file or directory.
                query_client_ip: Specifies the IP address from which the client accesses the file or directory.
                enabled: Specifies whether to enable or disable the filter. Filters are enabled by default and are deleted after 60 mins.
                query_enabled: Specifies whether to enable or disable the filter. Filters are enabled by default and are deleted after 60 mins.
                index: Position of the file access tracing filter.
                query_index: Position of the file access tracing filter.
                path: Specifies the path for which permission tracing can be applied. The value can be complete path from root of CIFS share or root of volume for NFS.
                query_path: Specifies the path for which permission tracing can be applied. The value can be complete path from root of CIFS share or root of volume for NFS.
                protocol: Specifies the protocol for which permission trace is required.
                query_protocol: Specifies the protocol for which permission trace is required.
                trace_allowed_ops: Specifies if the filter can trace file access denied and allowed events. The value of trace-allow is false by default, and it traces access denied events. The value is set to true for tracing access allowed events.
                query_trace_allowed_ops: Specifies if the filter can trace file access denied and allowed events. The value of trace-allow is false by default, and it traces access denied events. The value is set to true for tracing access allowed events.
                unix_user: Specifies the UNIX username whose access requests you want to trace. The filter would match only if the request is received with this user.
                query_unix_user: Specifies the UNIX username whose access requests you want to trace. The filter would match only if the request is received with this user.
                windows_user: Specifies the Windows username whose access requests you want to trace. The filter would match only if the request is received with this user.
                query_windows_user: Specifies the Windows username whose access requests you want to trace. The filter would match only if the request is received with this user.
            """

            kwargs = {}
            changes = {}
            if query_client_ip is not None:
                kwargs["client_ip"] = query_client_ip
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_index is not None:
                kwargs["index"] = query_index
            if query_path is not None:
                kwargs["path"] = query_path
            if query_protocol is not None:
                kwargs["protocol"] = query_protocol
            if query_trace_allowed_ops is not None:
                kwargs["trace_allowed_ops"] = query_trace_allowed_ops
            if query_unix_user is not None:
                kwargs["unix_user"] = query_unix_user
            if query_windows_user is not None:
                kwargs["windows_user"] = query_windows_user

            if client_ip is not None:
                changes["client_ip"] = client_ip
            if enabled is not None:
                changes["enabled"] = enabled
            if index is not None:
                changes["index"] = index
            if path is not None:
                changes["path"] = path
            if protocol is not None:
                changes["protocol"] = protocol
            if trace_allowed_ops is not None:
                changes["trace_allowed_ops"] = trace_allowed_ops
            if unix_user is not None:
                changes["unix_user"] = unix_user
            if windows_user is not None:
                changes["windows_user"] = windows_user

            if hasattr(FileAccessFilter, "find"):
                resource = FileAccessFilter.find(
                    **kwargs
                )
            else:
                resource = FileAccessFilter()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify FileAccessFilter: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes security trace filters.
### Related ONTAP commands
* `vserver security trace filter delete`
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file access filter delete")
        async def file_access_filter_delete(
        ) -> None:
            """Delete an instance of a FileAccessFilter resource

            Args:
                client_ip: Specifies the IP address from which the client accesses the file or directory.
                enabled: Specifies whether to enable or disable the filter. Filters are enabled by default and are deleted after 60 mins.
                index: Position of the file access tracing filter.
                path: Specifies the path for which permission tracing can be applied. The value can be complete path from root of CIFS share or root of volume for NFS.
                protocol: Specifies the protocol for which permission trace is required.
                trace_allowed_ops: Specifies if the filter can trace file access denied and allowed events. The value of trace-allow is false by default, and it traces access denied events. The value is set to true for tracing access allowed events.
                unix_user: Specifies the UNIX username whose access requests you want to trace. The filter would match only if the request is received with this user.
                windows_user: Specifies the Windows username whose access requests you want to trace. The filter would match only if the request is received with this user.
            """

            kwargs = {}
            if client_ip is not None:
                kwargs["client_ip"] = client_ip
            if enabled is not None:
                kwargs["enabled"] = enabled
            if index is not None:
                kwargs["index"] = index
            if path is not None:
                kwargs["path"] = path
            if protocol is not None:
                kwargs["protocol"] = protocol
            if trace_allowed_ops is not None:
                kwargs["trace_allowed_ops"] = trace_allowed_ops
            if unix_user is not None:
                kwargs["unix_user"] = unix_user
            if windows_user is not None:
                kwargs["windows_user"] = windows_user

            if hasattr(FileAccessFilter, "find"):
                resource = FileAccessFilter.find(
                    **kwargs
                )
            else:
                resource = FileAccessFilter()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete FileAccessFilter: %s" % err)


