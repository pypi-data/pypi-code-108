r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
You can use these API's to create file clones, retrieve split status and manage split loads. These endpoints are used for cloning files within a volume, without taking much of extra space. Child and parent clones shares the unchanged blocks of data.<br/>
A file clone split operation detach child clone from its parent. Split operations use space. To ensure that file clone create operation is not affected by split, file clone tokens are use to reserve space. API endpoints can be used to update the validity and space reserved by token.<br/>
## File clone APIs
The following APIs are used to perform the following operations:

* POST      /api/storage/file/clone
*  GET      /api/storage/file/clone/split-status
* PATCH     /api/storage/file/clone/split-loads/{node.uuid}
*  GET      /api/storage/file/clone/split-loads/{node.uuid}
*  GET      /api/storage/file/clone/split-loads
*  GET      /api/storage/file/clone/tokens/
* DELETE    /api/storage/file/clone/tokens/{node.uuid}/{token.uuid}
* PATCH     /api/storage/file/clone/tokens/{node.uuid}/{token.uuid}
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


__all__ = ["FileClone", "FileCloneSchema"]
__pdoc__ = {
    "FileCloneSchema.resource": False,
    "FileClone.file_clone_show": False,
    "FileClone.file_clone_create": False,
    "FileClone.file_clone_modify": False,
    "FileClone.file_clone_delete": False,
}


class FileCloneSchema(ResourceSchema):
    """The fields of the FileClone object"""

    autodelete = fields.Boolean(
        data_key="autodelete",
    )
    r""" Mark clone file for auto deletion. """

    destination_path = fields.Str(
        data_key="destination_path",
    )
    r""" Relative path of the clone/destination file in the volume.

Example: dest_file1, dir1/dest_file2 """

    is_backup = fields.Boolean(
        data_key="is_backup",
    )
    r""" Mark clone file for backup. """

    overwrite_destination = fields.Boolean(
        data_key="overwrite_destination",
    )
    r""" Destination file gets overwritten. """

    range = fields.List(fields.Str, data_key="range")
    r""" List of block ranges for sub-file cloning in the format "source-file-block-number:destination-file-block-number:block-count"

Example: [36605,73210] """

    source_path = fields.Str(
        data_key="source_path",
    )
    r""" Relative path of the source file in the volume.

Example: src_file1, dir1/src_file2, ./.snapshot/snap1/src_file3 """

    token_uuid = fields.Str(
        data_key="token_uuid",
    )
    r""" UUID of existing clone token with reserved split load. """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the file_clone. """

    @property
    def resource(self):
        return FileClone

    gettable_fields = [
        "autodelete",
        "destination_path",
        "is_backup",
        "overwrite_destination",
        "range",
        "source_path",
        "token_uuid",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """autodelete,destination_path,is_backup,overwrite_destination,range,source_path,token_uuid,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "autodelete",
        "destination_path",
        "is_backup",
        "overwrite_destination",
        "range",
        "source_path",
        "token_uuid",
        "volume.name",
        "volume.uuid",
    ]
    """autodelete,destination_path,is_backup,overwrite_destination,range,source_path,token_uuid,volume.name,volume.uuid,"""

    postable_fields = [
        "autodelete",
        "destination_path",
        "is_backup",
        "overwrite_destination",
        "range",
        "source_path",
        "token_uuid",
        "volume.name",
        "volume.uuid",
    ]
    """autodelete,destination_path,is_backup,overwrite_destination,range,source_path,token_uuid,volume.name,volume.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FileClone.get_collection(fields=field)]
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
            raise NetAppRestError("FileClone modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FileClone(Resource):
    r""" File clone """

    _schema = FileCloneSchema
    _path = "/api/storage/file/clone"




    @classmethod
    def post_collection(
        cls,
        records: Iterable["FileClone"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["FileClone"], NetAppResponse]:
        r"""Creates a clone of the file.
### Required Properties
* `source_path`
* `destination_path`
* `volume.uuid` and `volume.name` - Instance UUID and name of volume in which to create clone.
### Optional Properties
* `range` -  Required only in the case of a sub file clone.
* `autodelete` - Marks a cloned file for auto deletion.
* `backup` - Cloned file is used as a backup.
### Related Ontap commands
* `volume file clone create`
### Creating file clones
The POST operation is used to create file clones with the specified attributes in body. Set the `volume.name` and `volume.uuid` to identify the volume.<br/>
Set `source_path` and `destination_path` to identify the file path of original and copied file. In case of full file clone, the new file is created using `destination_path`.<br\>
In case of a sub file clone, set `range` in the format source-file-block-number:destination-file-block-number:block-count. The API returns an error for the following overlapping conditions: (a) if source and destination files are same and any of the source ranges  overlap with any of the destination ranges. (b) if any of the source ranges overlap amongst themselves. (c) if any of the destination ranges overlap amongst themselves. If not provided, full file cloning is assumed.<br/>
If set to `autodelete`, the cloned file is deleted when the volumes are full.<br\>
```
# The API:
curl -X POST "https://<mgmt_ip>/api/storage/file/clone" -H "accept: application/hal+json" -d '{"volume": {"name": "vol1",  "uuid": "40e0fdc5-c28f-11eb-8270-005056bbeb0b"}, "source_path": "f1", "destination_path": "f2_c1"}'
# The response:
{
  "job": {
    "uuid": "0d025fd9-c4dc-11eb-adb5-005056bbeb0b",
    "_links": {
       "self": {
         "href": "/api/cluster/jobs/0d025fd9-c4dc-11eb-adb5-005056bbeb0b"
       }
    }
  }
}
```
### Learn More
* [`DOC /storage/file/clone`]

### Learn more
* [`DOC /storage/file/clone`](#docs-storage-storage_file_clone)"""
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
        r"""Creates a clone of the file.
### Required Properties
* `source_path`
* `destination_path`
* `volume.uuid` and `volume.name` - Instance UUID and name of volume in which to create clone.
### Optional Properties
* `range` -  Required only in the case of a sub file clone.
* `autodelete` - Marks a cloned file for auto deletion.
* `backup` - Cloned file is used as a backup.
### Related Ontap commands
* `volume file clone create`
### Creating file clones
The POST operation is used to create file clones with the specified attributes in body. Set the `volume.name` and `volume.uuid` to identify the volume.<br/>
Set `source_path` and `destination_path` to identify the file path of original and copied file. In case of full file clone, the new file is created using `destination_path`.<br\>
In case of a sub file clone, set `range` in the format source-file-block-number:destination-file-block-number:block-count. The API returns an error for the following overlapping conditions: (a) if source and destination files are same and any of the source ranges  overlap with any of the destination ranges. (b) if any of the source ranges overlap amongst themselves. (c) if any of the destination ranges overlap amongst themselves. If not provided, full file cloning is assumed.<br/>
If set to `autodelete`, the cloned file is deleted when the volumes are full.<br\>
```
# The API:
curl -X POST "https://<mgmt_ip>/api/storage/file/clone" -H "accept: application/hal+json" -d '{"volume": {"name": "vol1",  "uuid": "40e0fdc5-c28f-11eb-8270-005056bbeb0b"}, "source_path": "f1", "destination_path": "f2_c1"}'
# The response:
{
  "job": {
    "uuid": "0d025fd9-c4dc-11eb-adb5-005056bbeb0b",
    "_links": {
       "self": {
         "href": "/api/cluster/jobs/0d025fd9-c4dc-11eb-adb5-005056bbeb0b"
       }
    }
  }
}
```
### Learn More
* [`DOC /storage/file/clone`]

### Learn more
* [`DOC /storage/file/clone`](#docs-storage-storage_file_clone)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file clone create")
        async def file_clone_create(
        ) -> ResourceTable:
            """Create an instance of a FileClone resource

            Args:
                autodelete: Mark clone file for auto deletion.
                destination_path: Relative path of the clone/destination file in the volume.
                is_backup: Mark clone file for backup.
                overwrite_destination: Destination file gets overwritten.
                range: List of block ranges for sub-file cloning in the format \"source-file-block-number:destination-file-block-number:block-count\"
                source_path: Relative path of the source file in the volume.
                token_uuid: UUID of existing clone token with reserved split load.
                volume: 
            """

            kwargs = {}
            if autodelete is not None:
                kwargs["autodelete"] = autodelete
            if destination_path is not None:
                kwargs["destination_path"] = destination_path
            if is_backup is not None:
                kwargs["is_backup"] = is_backup
            if overwrite_destination is not None:
                kwargs["overwrite_destination"] = overwrite_destination
            if range is not None:
                kwargs["range"] = range
            if source_path is not None:
                kwargs["source_path"] = source_path
            if token_uuid is not None:
                kwargs["token_uuid"] = token_uuid
            if volume is not None:
                kwargs["volume"] = volume

            resource = FileClone(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create FileClone: %s" % err)
            return [resource]




