r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

Use this API to display all Event Based Retention (EBR) operations and to apply an EBR policy on a specified volume.
### Examples
1. Displays all of the EBR operations:
   <br/>
   ```
   GET "/api/storage/snaplock/event-retention/operations"
   ```
   <br/>
2. Displays all completed EBR operations:
   <br/>
   ```
   GET "/api/storage/snaplock/event-retention/operations?state=completed"
   ```
   <br/>
3. Displays all completed EBR operations with filter set as volume.uuid:
   <br/>
   ```
   GET "/api/storage/snaplock/event-retention/operations?volume.uuid=b96f976e-404b-11e9-bff2-0050568e4dbe"
   ```
   <br/>
4. Displays all of the EBR operations with filter set as volume.name:
   <br/>
   ```
   GET "/api/storage/snaplock/event-retention/operations?volume.name=SLCVOL"
   ```
   <br/>
### Examples
1. Applies an EBR policy on a specific path:
   <br/>
   ```
   POST "/api/storage/snaplock/event-retention/operations" '{"volume.name":"SLCVOL", "policy.name":"p1day", "path":"/dir1/file.txt"}'
   ```
   <br/>
2. Applies an EBR policy on the complete volume:
   <br/>
   ```
   POST "/api/storage/snaplock/event-retention/operations" '{"volume.name":"SLCVOL", "policy.name":"p1day", "path":"/"}'
   ```
   <br/>
### Example
<br/>
```
DELETE "/api/storage/snaplock/event-retention/operations/16842999"
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


__all__ = ["EbrOperation", "EbrOperationSchema"]
__pdoc__ = {
    "EbrOperationSchema.resource": False,
    "EbrOperation.ebr_operation_show": False,
    "EbrOperation.ebr_operation_create": False,
    "EbrOperation.ebr_operation_modify": False,
    "EbrOperation.ebr_operation_delete": False,
}


class EbrOperationSchema(ResourceSchema):
    """The fields of the EbrOperation object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the ebr_operation. """

    id = Size(
        data_key="id",
    )
    r""" Operation ID

Example: 16842759 """

    num_files_failed = Size(
        data_key="num_files_failed",
    )
    r""" Specifies the number of files on which the application of EBR policy failed.

Example: 0 """

    num_files_processed = Size(
        data_key="num_files_processed",
    )
    r""" Specifies the number of files on which EBR policy was applied successfully.

Example: 50 """

    num_files_skipped = Size(
        data_key="num_files_skipped",
    )
    r""" Specifies the number of files on which the application of EBR policy was skipped.

Example: 2 """

    num_inodes_ignored = Size(
        data_key="num_inodes_ignored",
    )
    r""" Specifies the number of inodes on which the application of EBR policy was not attempted because they were not regular files.

Example: 2 """

    path = fields.Str(
        data_key="path",
    )
    r""" The path for the EBR operation. Specifies the path relative to the output volume root, of the form "/path". The path can be path to a file or a directory.

Example: /dir1/file """

    policy = fields.Nested("netapp_ontap.resources.snaplock_retention_policy.SnaplockRetentionPolicySchema", data_key="policy", unknown=EXCLUDE)
    r""" The policy field of the ebr_operation. """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['unknown', 'in_progress', 'failed', 'aborting', 'completed']),
    )
    r""" Specifies the operation status of an EBR operation.

Valid choices:

* unknown
* in_progress
* failed
* aborting
* completed """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the ebr_operation. """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the ebr_operation. """

    @property
    def resource(self):
        return EbrOperation

    gettable_fields = [
        "links",
        "id",
        "num_files_failed",
        "num_files_processed",
        "num_files_skipped",
        "num_inodes_ignored",
        "path",
        "policy",
        "state",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,id,num_files_failed,num_files_processed,num_files_skipped,num_inodes_ignored,path,policy,state,svm.links,svm.name,svm.uuid,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "path",
        "policy",
        "svm.name",
        "svm.uuid",
        "volume.name",
        "volume.uuid",
    ]
    """path,policy,svm.name,svm.uuid,volume.name,volume.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in EbrOperation.get_collection(fields=field)]
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
            raise NetAppRestError("EbrOperation modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class EbrOperation(Resource):
    """Allows interaction with EbrOperation objects on the host"""

    _schema = EbrOperationSchema
    _path = "/api/storage/snaplock/event-retention/operations"
    _keys = ["id"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a list of all EBR operations.
### Related ONTAP commands
* `snaplock event-retention show`
### Learn more
* [`DOC /storage/snaplock/event-retention/operations`](#docs-snaplock-storage_snaplock_event-retention_operations)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ebr operation show")
        def ebr_operation_show(
            fields: List[Choices.define(["id", "num_files_failed", "num_files_processed", "num_files_skipped", "num_inodes_ignored", "path", "state", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of EbrOperation resources

            Args:
                id: Operation ID
                num_files_failed: Specifies the number of files on which the application of EBR policy failed.
                num_files_processed: Specifies the number of files on which EBR policy was applied successfully.
                num_files_skipped: Specifies the number of files on which the application of EBR policy was skipped.
                num_inodes_ignored: Specifies the number of inodes on which the application of EBR policy was not attempted because they were not regular files.
                path: The path for the EBR operation. Specifies the path relative to the output volume root, of the form \"/path\". The path can be path to a file or a directory.
                state: Specifies the operation status of an EBR operation.
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
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return EbrOperation.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all EbrOperation resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["EbrOperation"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["EbrOperation"], NetAppResponse]:
        r"""Creates an EBR policy.
### Required properties
* `path` - Path of the file.
* `policy.name` - Name of the EBR policy.
### Related ONTAP commands
* `snaplock event-retention apply`
### Learn more
* [`DOC /storage/snaplock/event-retention/operations`](#docs-snaplock-storage_snaplock_event-retention_operations)
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
        records: Iterable["EbrOperation"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Aborts an ongoing EBR operation.
### Related ONTAP commands
* `snaplock event-retention abort`
### Learn more
* [`DOC /storage/snaplock/event-retention/operations`](#docs-snaplock-storage_snaplock_event-retention_operations)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a list of all EBR operations.
### Related ONTAP commands
* `snaplock event-retention show`
### Learn more
* [`DOC /storage/snaplock/event-retention/operations`](#docs-snaplock-storage_snaplock_event-retention_operations)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a list of attributes for an EBR operation.
### Related ONTAP commands
* `snaplock event-retention show`
### Learn more
* [`DOC /storage/snaplock/event-retention/operations`](#docs-snaplock-storage_snaplock_event-retention_operations)
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
        r"""Creates an EBR policy.
### Required properties
* `path` - Path of the file.
* `policy.name` - Name of the EBR policy.
### Related ONTAP commands
* `snaplock event-retention apply`
### Learn more
* [`DOC /storage/snaplock/event-retention/operations`](#docs-snaplock-storage_snaplock_event-retention_operations)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ebr operation create")
        async def ebr_operation_create(
        ) -> ResourceTable:
            """Create an instance of a EbrOperation resource

            Args:
                links: 
                id: Operation ID
                num_files_failed: Specifies the number of files on which the application of EBR policy failed.
                num_files_processed: Specifies the number of files on which EBR policy was applied successfully.
                num_files_skipped: Specifies the number of files on which the application of EBR policy was skipped.
                num_inodes_ignored: Specifies the number of inodes on which the application of EBR policy was not attempted because they were not regular files.
                path: The path for the EBR operation. Specifies the path relative to the output volume root, of the form \"/path\". The path can be path to a file or a directory.
                policy: 
                state: Specifies the operation status of an EBR operation.
                svm: 
                volume: 
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
            if policy is not None:
                kwargs["policy"] = policy
            if state is not None:
                kwargs["state"] = state
            if svm is not None:
                kwargs["svm"] = svm
            if volume is not None:
                kwargs["volume"] = volume

            resource = EbrOperation(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create EbrOperation: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Aborts an ongoing EBR operation.
### Related ONTAP commands
* `snaplock event-retention abort`
### Learn more
* [`DOC /storage/snaplock/event-retention/operations`](#docs-snaplock-storage_snaplock_event-retention_operations)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ebr operation delete")
        async def ebr_operation_delete(
        ) -> None:
            """Delete an instance of a EbrOperation resource

            Args:
                id: Operation ID
                num_files_failed: Specifies the number of files on which the application of EBR policy failed.
                num_files_processed: Specifies the number of files on which EBR policy was applied successfully.
                num_files_skipped: Specifies the number of files on which the application of EBR policy was skipped.
                num_inodes_ignored: Specifies the number of inodes on which the application of EBR policy was not attempted because they were not regular files.
                path: The path for the EBR operation. Specifies the path relative to the output volume root, of the form \"/path\". The path can be path to a file or a directory.
                state: Specifies the operation status of an EBR operation.
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

            if hasattr(EbrOperation, "find"):
                resource = EbrOperation.find(
                    **kwargs
                )
            else:
                resource = EbrOperation()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete EbrOperation: %s" % err)


