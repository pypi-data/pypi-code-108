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


__all__ = ["FileCopy", "FileCopySchema"]
__pdoc__ = {
    "FileCopySchema.resource": False,
    "FileCopy.file_copy_show": False,
    "FileCopy.file_copy_create": False,
    "FileCopy.file_copy_modify": False,
    "FileCopy.file_copy_delete": False,
}


class FileCopySchema(ResourceSchema):
    """The fields of the FileCopy object"""

    cutover_time = Size(
        data_key="cutover_time",
    )
    r""" The maximum amount of time (in seconds) that the source can be quiesced before a destination file must be made available for read-write traffic.

Example: 10 """

    files_to_copy = fields.List(fields.Nested("netapp_ontap.models.file_copy_files_to_copy.FileCopyFilesToCopySchema", unknown=EXCLUDE), data_key="files_to_copy")
    r""" A list of source files along with the destinations they are copied to. If the terminal path component of the destination is a directory, then the source file's basename is replicated in that directory. """

    hold_quiescence = fields.Boolean(
        data_key="hold_quiescence",
    )
    r""" Specifies whether the source file should be held quiescent for the duration of the copy operation. """

    max_throughput = Size(
        data_key="max_throughput",
    )
    r""" The maximum amount of data (in bytes) that can be transferred per second in support of this operation. """

    reference_cutover_time = Size(
        data_key="reference_cutover_time",
    )
    r""" The maximum amount of time (in seconds) that the source reference file can be quiesced before the corresponding destination file must be made available for read-write traffic.

Example: 10 """

    reference_file = fields.Nested("netapp_ontap.models.file_copy_reference_file.FileCopyReferenceFileSchema", data_key="reference_file", unknown=EXCLUDE)
    r""" The reference_file field of the file_copy. """

    @property
    def resource(self):
        return FileCopy

    gettable_fields = [
        "cutover_time",
        "files_to_copy",
        "hold_quiescence",
        "max_throughput",
        "reference_cutover_time",
        "reference_file",
    ]
    """cutover_time,files_to_copy,hold_quiescence,max_throughput,reference_cutover_time,reference_file,"""

    patchable_fields = [
        "cutover_time",
        "files_to_copy",
        "hold_quiescence",
        "max_throughput",
        "reference_cutover_time",
        "reference_file",
    ]
    """cutover_time,files_to_copy,hold_quiescence,max_throughput,reference_cutover_time,reference_file,"""

    postable_fields = [
        "cutover_time",
        "files_to_copy",
        "hold_quiescence",
        "max_throughput",
        "reference_cutover_time",
        "reference_file",
    ]
    """cutover_time,files_to_copy,hold_quiescence,max_throughput,reference_cutover_time,reference_file,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FileCopy.get_collection(fields=field)]
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
            raise NetAppRestError("FileCopy modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FileCopy(Resource):
    r""" File copy """

    _schema = FileCopySchema
    _path = "/api/storage/file/copy"




    @classmethod
    def post_collection(
        cls,
        records: Iterable["FileCopy"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["FileCopy"], NetAppResponse]:
        r"""Starts a file copy operation. Only supported on flexible volumes.
## Required properties
* `files_to_copy` - List of files with the destination they are to be copied to.
## Default property values
* `cutover_time` - _10_
* `hold_quiescence` - _false_
* `max_throughput` - _0_
* `reference_cutover_time` - _10_
## Related ONTAP commands
* `volume file copy start`
## Examples
### Copying two files
The POST request is used to copy file(s).
```
# The API:
/api/storage/file/copy
# The call:
curl -X POST  "https://<mgmt-ip>/api/storage/file/copy" -H "accept: application/hal+json" -d '{"files_to_copy":[{"source":{"volume":{"name":"vol_a"},"svm":{"name":"vs0"},"path":"d1/src_f1"},"destination":{"volume":{"name":"vol_a"},"svm":{"name":"vs0"},"path":"d1/dst_f1"}}, {"source":{"volume":{"name":"vol_a"},"svm":{"name":"vs0"},"path":"d1/src_f2"},"destination":{"volume":{"name":"vol_a"},"svm":{"name":"vs0"},"path":"d1/dst_f2"}}]}'
# The response:
{
  "job": {
    "uuid": "b89bc5dd-94a3-11e8-a7a3-0050568edf84",
    "_links": {
       "self": {
         "href": "/api/cluster/jobs/b89bc5dd-94a3-11e8-a7a3-0050568edf84"
       }
     }
   }
}
```
"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)




    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Starts a file copy operation. Only supported on flexible volumes.
## Required properties
* `files_to_copy` - List of files with the destination they are to be copied to.
## Default property values
* `cutover_time` - _10_
* `hold_quiescence` - _false_
* `max_throughput` - _0_
* `reference_cutover_time` - _10_
## Related ONTAP commands
* `volume file copy start`
## Examples
### Copying two files
The POST request is used to copy file(s).
```
# The API:
/api/storage/file/copy
# The call:
curl -X POST  "https://<mgmt-ip>/api/storage/file/copy" -H "accept: application/hal+json" -d '{"files_to_copy":[{"source":{"volume":{"name":"vol_a"},"svm":{"name":"vs0"},"path":"d1/src_f1"},"destination":{"volume":{"name":"vol_a"},"svm":{"name":"vs0"},"path":"d1/dst_f1"}}, {"source":{"volume":{"name":"vol_a"},"svm":{"name":"vs0"},"path":"d1/src_f2"},"destination":{"volume":{"name":"vol_a"},"svm":{"name":"vs0"},"path":"d1/dst_f2"}}]}'
# The response:
{
  "job": {
    "uuid": "b89bc5dd-94a3-11e8-a7a3-0050568edf84",
    "_links": {
       "self": {
         "href": "/api/cluster/jobs/b89bc5dd-94a3-11e8-a7a3-0050568edf84"
       }
     }
   }
}
```
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file copy create")
        async def file_copy_create(
        ) -> ResourceTable:
            """Create an instance of a FileCopy resource

            Args:
                cutover_time: The maximum amount of time (in seconds) that the source can be quiesced before a destination file must be made available for read-write traffic.
                files_to_copy: A list of source files along with the destinations they are copied to. If the terminal path component of the destination is a directory, then the source file's basename is replicated in that directory.
                hold_quiescence: Specifies whether the source file should be held quiescent for the duration of the copy operation.
                max_throughput: The maximum amount of data (in bytes) that can be transferred per second in support of this operation.
                reference_cutover_time: The maximum amount of time (in seconds) that the source reference file can be quiesced before the corresponding destination file must be made available for read-write traffic.
                reference_file: 
            """

            kwargs = {}
            if cutover_time is not None:
                kwargs["cutover_time"] = cutover_time
            if files_to_copy is not None:
                kwargs["files_to_copy"] = files_to_copy
            if hold_quiescence is not None:
                kwargs["hold_quiescence"] = hold_quiescence
            if max_throughput is not None:
                kwargs["max_throughput"] = max_throughput
            if reference_cutover_time is not None:
                kwargs["reference_cutover_time"] = reference_cutover_time
            if reference_file is not None:
                kwargs["reference_file"] = reference_file

            resource = FileCopy(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create FileCopy: %s" % err)
            return [resource]




