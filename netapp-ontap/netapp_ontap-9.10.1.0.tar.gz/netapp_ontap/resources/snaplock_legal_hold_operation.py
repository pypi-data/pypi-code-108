r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

Manages the legal-hold operations for the specified litigation ID.
### Examples
1. Adds a Legal-Hold.
   <br/>
   ```
   POST "/api/storage/snaplock/litigations/f8a67b60-4461-11e9-b327-0050568ebef5:l1/operations" '{"type" : "begin", "path" : "/a.txt"}'
   ```
   <br/>
2. Removes a Legal-Hold.
   <br/>
   ```
   POST "/api/storage/snaplock/litigations/f8a67b60-4461-11e9-b327-0050568ebef5:l1/operations" '{"type" : "end", "path" : "/a.txt"}'
   ```
   <br/>
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


__all__ = ["SnaplockLegalHoldOperation", "SnaplockLegalHoldOperationSchema"]
__pdoc__ = {
    "SnaplockLegalHoldOperationSchema.resource": False,
    "SnaplockLegalHoldOperation.snaplock_legal_hold_operation_show": False,
    "SnaplockLegalHoldOperation.snaplock_legal_hold_operation_create": False,
    "SnaplockLegalHoldOperation.snaplock_legal_hold_operation_modify": False,
    "SnaplockLegalHoldOperation.snaplock_legal_hold_operation_delete": False,
}


class SnaplockLegalHoldOperationSchema(ResourceSchema):
    """The fields of the SnaplockLegalHoldOperation object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the snaplock_legal_hold_operation. """

    id = Size(
        data_key="id",
    )
    r""" Operation ID.

Example: 16842759 """

    num_files_failed = fields.Str(
        data_key="num_files_failed",
    )
    r""" Specifies the number of files on which legal-hold operation failed.

Example: 0 """

    num_files_processed = fields.Str(
        data_key="num_files_processed",
    )
    r""" Specifies the number of files on which legal-hold operation was successful.

Example: 30 """

    num_files_skipped = fields.Str(
        data_key="num_files_skipped",
    )
    r""" Specifies the number of files on which legal-hold begin operation was skipped. The legal-hold begin operation is skipped on a file if it is already under hold for a given litigation.

Example: 10 """

    num_inodes_ignored = fields.Str(
        data_key="num_inodes_ignored",
    )
    r""" Specifies the number of inodes on which the legal-hold operation was not attempted because they were not regular files.

Example: 10 """

    path = fields.Str(
        data_key="path",
    )
    r""" Specifies the path on which legal-hold operation is applied.

Example: /dir1 """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['in_progress', 'failed', 'aborting', 'completed']),
    )
    r""" Specifies the status of legal-hold operation.

Valid choices:

* in_progress
* failed
* aborting
* completed """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['begin', 'end']),
    )
    r""" Specifies the type of legal-hold operation.

Valid choices:

* begin
* end """

    @property
    def resource(self):
        return SnaplockLegalHoldOperation

    gettable_fields = [
        "links",
        "id",
        "num_files_failed",
        "num_files_processed",
        "num_files_skipped",
        "num_inodes_ignored",
        "path",
        "state",
        "type",
    ]
    """links,id,num_files_failed,num_files_processed,num_files_skipped,num_inodes_ignored,path,state,type,"""

    patchable_fields = [
        "type",
    ]
    """type,"""

    postable_fields = [
        "path",
    ]
    """path,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SnaplockLegalHoldOperation.get_collection(fields=field)]
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
            raise NetAppRestError("SnaplockLegalHoldOperation modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SnaplockLegalHoldOperation(Resource):
    """Allows interaction with SnaplockLegalHoldOperation objects on the host"""

    _schema = SnaplockLegalHoldOperationSchema
    _path = "/api/storage/snaplock/litigations/{litigation[id]}/operations"
    _keys = ["litigation.id", "id"]




    @classmethod
    def post_collection(
        cls,
        records: Iterable["SnaplockLegalHoldOperation"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["SnaplockLegalHoldOperation"], NetAppResponse]:
        r"""Creates or removes litigations for the specified path.
### Required properties
* `type` - Legal-Hold operation type.
* `path` - Litigation path.
### Related ONTAP commands
* `snaplock legal-hold begin`
* `snaplock legal-hold end`
### Learn more
* [`DOC /storage/snaplock/litigations/{litigation.id}/operations`](#docs-snaplock-storage_snaplock_litigations_{litigation.id}_operations)
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
        records: Iterable["SnaplockLegalHoldOperation"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Aborts the ongoing legal-hold operation. An abort does not rollback any changes already made. You must re-run begin or end for cleanup.
### Related ONTAP commands
* `snaplock legal-hold abort`
### Example
<br/>
```
DELETE "/api/storage/snaplock/litigations/f8a67b60-4461-11e9-b327-0050568ebef5:l1/operations/16908292"
```
<br/>
### Learn more
* [`DOC /storage/snaplock/litigations/{litigation.id}/operations`](#docs-snaplock-storage_snaplock_litigations_{litigation.id}_operations)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)


    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the status of legal-hold for the specified operation ID.
### Related ONTAP commands
* `snaplock legal-hold show`
### Learn more
* [`DOC /storage/snaplock/litigations/{litigation.id}/operations`](#docs-snaplock-storage_snaplock_litigations_{litigation.id}_operations)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock legal hold operation show")
        def snaplock_legal_hold_operation_show(
            litigation_id,
            id: Choices.define(_get_field_list("id"), cache_choices=True, inexact=True)=None,
            num_files_failed: Choices.define(_get_field_list("num_files_failed"), cache_choices=True, inexact=True)=None,
            num_files_processed: Choices.define(_get_field_list("num_files_processed"), cache_choices=True, inexact=True)=None,
            num_files_skipped: Choices.define(_get_field_list("num_files_skipped"), cache_choices=True, inexact=True)=None,
            num_inodes_ignored: Choices.define(_get_field_list("num_inodes_ignored"), cache_choices=True, inexact=True)=None,
            path: Choices.define(_get_field_list("path"), cache_choices=True, inexact=True)=None,
            state: Choices.define(_get_field_list("state"), cache_choices=True, inexact=True)=None,
            type: Choices.define(_get_field_list("type"), cache_choices=True, inexact=True)=None,
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single SnaplockLegalHoldOperation resource

            Args:
                id: Operation ID.
                num_files_failed: Specifies the number of files on which legal-hold operation failed.
                num_files_processed: Specifies the number of files on which legal-hold operation was successful.
                num_files_skipped: Specifies the number of files on which legal-hold begin operation was skipped. The legal-hold begin operation is skipped on a file if it is already under hold for a given litigation.
                num_inodes_ignored: Specifies the number of inodes on which the legal-hold operation was not attempted because they were not regular files.
                path: Specifies the path on which legal-hold operation is applied.
                state: Specifies the status of legal-hold operation.
                type: Specifies the type of legal-hold operation.
            """

            kwargs = {}
            if id is not None:
                kwargs["id"] = id
            if num_files_failed is not None:
                kwargs["num_files_failed"] = num_files_failed
            if num_files_processed is not None:
                kwargs["num_files_processed"] = num_files_processed
            if num_files_skipped is not None:
                kwargs["num_files_skipped"] = num_files_skipped
            if num_inodes_ignored is not None:
                kwargs["num_inodes_ignored"] = num_inodes_ignored
            if path is not None:
                kwargs["path"] = path
            if state is not None:
                kwargs["state"] = state
            if type is not None:
                kwargs["type"] = type
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = SnaplockLegalHoldOperation(
                litigation_id,
                **kwargs
            )
            resource.get()
            return [resource]

    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates or removes litigations for the specified path.
### Required properties
* `type` - Legal-Hold operation type.
* `path` - Litigation path.
### Related ONTAP commands
* `snaplock legal-hold begin`
* `snaplock legal-hold end`
### Learn more
* [`DOC /storage/snaplock/litigations/{litigation.id}/operations`](#docs-snaplock-storage_snaplock_litigations_{litigation.id}_operations)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock legal hold operation create")
        async def snaplock_legal_hold_operation_create(
            litigation_id,
            links: dict = None,
            id: Size = None,
            num_files_failed: str = None,
            num_files_processed: str = None,
            num_files_skipped: str = None,
            num_inodes_ignored: str = None,
            path: str = None,
            state: str = None,
            type: str = None,
        ) -> ResourceTable:
            """Create an instance of a SnaplockLegalHoldOperation resource

            Args:
                links: 
                id: Operation ID.
                num_files_failed: Specifies the number of files on which legal-hold operation failed.
                num_files_processed: Specifies the number of files on which legal-hold operation was successful.
                num_files_skipped: Specifies the number of files on which legal-hold begin operation was skipped. The legal-hold begin operation is skipped on a file if it is already under hold for a given litigation.
                num_inodes_ignored: Specifies the number of inodes on which the legal-hold operation was not attempted because they were not regular files.
                path: Specifies the path on which legal-hold operation is applied.
                state: Specifies the status of legal-hold operation.
                type: Specifies the type of legal-hold operation.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if id is not None:
                kwargs["id"] = id
            if num_files_failed is not None:
                kwargs["num_files_failed"] = num_files_failed
            if num_files_processed is not None:
                kwargs["num_files_processed"] = num_files_processed
            if num_files_skipped is not None:
                kwargs["num_files_skipped"] = num_files_skipped
            if num_inodes_ignored is not None:
                kwargs["num_inodes_ignored"] = num_inodes_ignored
            if path is not None:
                kwargs["path"] = path
            if state is not None:
                kwargs["state"] = state
            if type is not None:
                kwargs["type"] = type

            resource = SnaplockLegalHoldOperation(
                litigation_id,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SnaplockLegalHoldOperation: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Aborts the ongoing legal-hold operation. An abort does not rollback any changes already made. You must re-run begin or end for cleanup.
### Related ONTAP commands
* `snaplock legal-hold abort`
### Example
<br/>
```
DELETE "/api/storage/snaplock/litigations/f8a67b60-4461-11e9-b327-0050568ebef5:l1/operations/16908292"
```
<br/>
### Learn more
* [`DOC /storage/snaplock/litigations/{litigation.id}/operations`](#docs-snaplock-storage_snaplock_litigations_{litigation.id}_operations)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock legal hold operation delete")
        async def snaplock_legal_hold_operation_delete(
            litigation_id,
            id: Size = None,
            num_files_failed: str = None,
            num_files_processed: str = None,
            num_files_skipped: str = None,
            num_inodes_ignored: str = None,
            path: str = None,
            state: str = None,
            type: str = None,
        ) -> None:
            """Delete an instance of a SnaplockLegalHoldOperation resource

            Args:
                id: Operation ID.
                num_files_failed: Specifies the number of files on which legal-hold operation failed.
                num_files_processed: Specifies the number of files on which legal-hold operation was successful.
                num_files_skipped: Specifies the number of files on which legal-hold begin operation was skipped. The legal-hold begin operation is skipped on a file if it is already under hold for a given litigation.
                num_inodes_ignored: Specifies the number of inodes on which the legal-hold operation was not attempted because they were not regular files.
                path: Specifies the path on which legal-hold operation is applied.
                state: Specifies the status of legal-hold operation.
                type: Specifies the type of legal-hold operation.
            """

            kwargs = {}
            if id is not None:
                kwargs["id"] = id
            if num_files_failed is not None:
                kwargs["num_files_failed"] = num_files_failed
            if num_files_processed is not None:
                kwargs["num_files_processed"] = num_files_processed
            if num_files_skipped is not None:
                kwargs["num_files_skipped"] = num_files_skipped
            if num_inodes_ignored is not None:
                kwargs["num_inodes_ignored"] = num_inodes_ignored
            if path is not None:
                kwargs["path"] = path
            if state is not None:
                kwargs["state"] = state
            if type is not None:
                kwargs["type"] = type

            if hasattr(SnaplockLegalHoldOperation, "find"):
                resource = SnaplockLegalHoldOperation.find(
                    litigation_id,
                    **kwargs
                )
            else:
                resource = SnaplockLegalHoldOperation(litigation_id,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete SnaplockLegalHoldOperation: %s" % err)


