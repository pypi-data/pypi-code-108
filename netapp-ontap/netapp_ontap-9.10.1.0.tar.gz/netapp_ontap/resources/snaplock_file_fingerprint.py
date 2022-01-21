r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

Use this API to view key information about files and volumes, including the file type (regular, WORM, or WORM appendable), the volume expiration date, and so on.
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


__all__ = ["SnaplockFileFingerprint", "SnaplockFileFingerprintSchema"]
__pdoc__ = {
    "SnaplockFileFingerprintSchema.resource": False,
    "SnaplockFileFingerprint.snaplock_file_fingerprint_show": False,
    "SnaplockFileFingerprint.snaplock_file_fingerprint_create": False,
    "SnaplockFileFingerprint.snaplock_file_fingerprint_modify": False,
    "SnaplockFileFingerprint.snaplock_file_fingerprint_delete": False,
}


class SnaplockFileFingerprintSchema(ResourceSchema):
    """The fields of the SnaplockFileFingerprint object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the snaplock_file_fingerprint. """

    algorithm = fields.Str(
        data_key="algorithm",
        validate=enum_validation(['md5', 'sha256']),
    )
    r""" The digest algorithm which is used for the fingerprint computation

Valid choices:

* md5
* sha256 """

    data_fingerprint = fields.Str(
        data_key="data_fingerprint",
    )
    r""" The digest value of data of the file. The fingerprint is base64 encoded. This field is not included if the scope is metadata-only.

Example: MOFJVevxNSJm3C/4Bn5oEEYH51CrudOzZYK4r5Cfy1g= """

    file_size = Size(
        data_key="file_size",
    )
    r""" The size of the file in bytes.

Example: 1048576 """

    file_type = fields.Str(
        data_key="file_type",
        validate=enum_validation(['worm', 'worm_appendable', 'worm_active_log', 'worm_log', 'regular']),
    )
    r""" The type of the file.

Valid choices:

* worm
* worm_appendable
* worm_active_log
* worm_log
* regular """

    id = Size(
        data_key="id",
    )
    r""" A unique identifier for the fingerprint operation

Example: 17039367 """

    metadata_fingerprint = fields.Str(
        data_key="metadata_fingerprint",
    )
    r""" The digest value of metadata of the file. The metadata fingerprint is calculated for file size, file ctime, file mtime, file crtime, file retention time, file uid, file gid, and file type. The fingerprint is base64 encoded. This field is not included if the scope is data-only.

Example: 8iMjqJXiNcqgXT5XuRhLiEwIrJEihDmwS0hrexnjgmc= """

    path = fields.Str(
        data_key="path",
    )
    r""" Specifies the path on which file fingerprint operation is running or has completed. Specifies the path relative to the output volume root, of the form "/path". The path can be path to a file or a directory.

Example: /homedir/dir1 """

    scope = fields.Str(
        data_key="scope",
        validate=enum_validation(['data_and_metadata', 'data_only', 'metadata_only']),
    )
    r""" The scope of the file which is used for the fingerprint computation

Valid choices:

* data_and_metadata
* data_only
* metadata_only """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['in_progress', 'failed', 'aborting', 'completed']),
    )
    r""" Specifies the status of fingerprint operation.

Valid choices:

* in_progress
* failed
* aborting
* completed """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the snaplock_file_fingerprint. """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the snaplock_file_fingerprint. """

    @property
    def resource(self):
        return SnaplockFileFingerprint

    gettable_fields = [
        "links",
        "algorithm",
        "data_fingerprint",
        "file_size",
        "file_type",
        "id",
        "metadata_fingerprint",
        "path",
        "scope",
        "state",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,algorithm,data_fingerprint,file_size,file_type,id,metadata_fingerprint,path,scope,state,svm.links,svm.name,svm.uuid,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "algorithm",
        "path",
        "svm.name",
        "svm.uuid",
        "volume.name",
        "volume.uuid",
    ]
    """algorithm,path,svm.name,svm.uuid,volume.name,volume.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SnaplockFileFingerprint.get_collection(fields=field)]
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
            raise NetAppRestError("SnaplockFileFingerprint modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SnaplockFileFingerprint(Resource):
    """Allows interaction with SnaplockFileFingerprint objects on the host"""

    _schema = SnaplockFileFingerprintSchema
    _path = "/api/storage/snaplock/file-fingerprints"
    _keys = ["id"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a list of all the fingerprint operations of the specified SVM and volume.
### Related ONTAP commands
* `volume file fingerprint show`
### Example
<br/>
```
GET "/api/storage/snaplock/file-fingerprints/?svm.uuid=23940494-3f3a-11e9-8675-0050568e8f89&volume.uuid=36cdb58c-3f3a-11e9-8675-0050568e8f89"
```
<br/>
### Learn more
* [`DOC /storage/snaplock/file-fingerprints`](#docs-snaplock-storage_snaplock_file-fingerprints)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock file fingerprint show")
        def snaplock_file_fingerprint_show(
            fields: List[Choices.define(["algorithm", "data_fingerprint", "file_size", "file_type", "id", "metadata_fingerprint", "path", "scope", "state", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SnaplockFileFingerprint resources

            Args:
                algorithm: The digest algorithm which is used for the fingerprint computation
                data_fingerprint: The digest value of data of the file. The fingerprint is base64 encoded. This field is not included if the scope is metadata-only.
                file_size: The size of the file in bytes.
                file_type: The type of the file.
                id: A unique identifier for the fingerprint operation
                metadata_fingerprint: The digest value of metadata of the file. The metadata fingerprint is calculated for file size, file ctime, file mtime, file crtime, file retention time, file uid, file gid, and file type. The fingerprint is base64 encoded. This field is not included if the scope is data-only.
                path: Specifies the path on which file fingerprint operation is running or has completed. Specifies the path relative to the output volume root, of the form \"/path\". The path can be path to a file or a directory.
                scope: The scope of the file which is used for the fingerprint computation
                state: Specifies the status of fingerprint operation.
            """

            kwargs = {}
            if algorithm is not None:
                kwargs["algorithm"] = algorithm
            if data_fingerprint is not None:
                kwargs["data_fingerprint"] = data_fingerprint
            if file_size is not None:
                kwargs["file_size"] = file_size
            if file_type is not None:
                kwargs["file_type"] = file_type
            if id is not None:
                kwargs["id"] = id
            if metadata_fingerprint is not None:
                kwargs["metadata_fingerprint"] = metadata_fingerprint
            if path is not None:
                kwargs["path"] = path
            if scope is not None:
                kwargs["scope"] = scope
            if state is not None:
                kwargs["state"] = state
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SnaplockFileFingerprint.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SnaplockFileFingerprint resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["SnaplockFileFingerprint"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["SnaplockFileFingerprint"], NetAppResponse]:
        r"""Creates a fingerprint computation session on the file and returns a session-id. This session-id is a unique identifier that you can use to retrieve the progress of an ongoing fingerprint operation. When the operation is complete, you can use the session-id to retrieve the complete fingerprint output for the file .
### Required properties
* `svm.uuid` or `svm.name` - Name or UUID of the SVM.
* `volume.name` or `volume.uuid` - Name or UUID of the volume.
* `path` - Path of the file.
### Default property values
If not specified in POST, the follow default property values are assigned:
* `algorithm` - _md5_
### Related ONTAP commands
* `volume file fingerprint start`
### Example
<br/>
```
POST "/api/storage/snaplock/file-fingerprints" '{"svm":{"uuid":"23940494-3f3a-11e9-8675-0050568e8f89"},"volume": {"uuid":"26cdb58c-3f3a-11e9-8675-0050568e8f89"},"path":"/vol/a1.txt","algorithm":"md5"}'
```
<br/>
### Learn more
* [`DOC /storage/snaplock/file-fingerprints`](#docs-snaplock-storage_snaplock_file-fingerprints)
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
        records: Iterable["SnaplockFileFingerprint"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Aborts an in-progress fingerprint operation. This API takes session-id as input and aborts the fingerprint operation that is associated with the specified session-id.
### Related ONTAP commands
* `volume file fingerprint abort`
### Learn more
* [`DOC /storage/snaplock/file-fingerprints`](#docs-snaplock-storage_snaplock_file-fingerprints)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a list of all the fingerprint operations of the specified SVM and volume.
### Related ONTAP commands
* `volume file fingerprint show`
### Example
<br/>
```
GET "/api/storage/snaplock/file-fingerprints/?svm.uuid=23940494-3f3a-11e9-8675-0050568e8f89&volume.uuid=36cdb58c-3f3a-11e9-8675-0050568e8f89"
```
<br/>
### Learn more
* [`DOC /storage/snaplock/file-fingerprints`](#docs-snaplock-storage_snaplock_file-fingerprints)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the file fingerprint information for a specific session ID.
### Related ONTAP commands
* `volume file fingerprint dump`
### Learn more
* [`DOC /storage/snaplock/file-fingerprints`](#docs-snaplock-storage_snaplock_file-fingerprints)
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
        r"""Creates a fingerprint computation session on the file and returns a session-id. This session-id is a unique identifier that you can use to retrieve the progress of an ongoing fingerprint operation. When the operation is complete, you can use the session-id to retrieve the complete fingerprint output for the file .
### Required properties
* `svm.uuid` or `svm.name` - Name or UUID of the SVM.
* `volume.name` or `volume.uuid` - Name or UUID of the volume.
* `path` - Path of the file.
### Default property values
If not specified in POST, the follow default property values are assigned:
* `algorithm` - _md5_
### Related ONTAP commands
* `volume file fingerprint start`
### Example
<br/>
```
POST "/api/storage/snaplock/file-fingerprints" '{"svm":{"uuid":"23940494-3f3a-11e9-8675-0050568e8f89"},"volume": {"uuid":"26cdb58c-3f3a-11e9-8675-0050568e8f89"},"path":"/vol/a1.txt","algorithm":"md5"}'
```
<br/>
### Learn more
* [`DOC /storage/snaplock/file-fingerprints`](#docs-snaplock-storage_snaplock_file-fingerprints)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock file fingerprint create")
        async def snaplock_file_fingerprint_create(
        ) -> ResourceTable:
            """Create an instance of a SnaplockFileFingerprint resource

            Args:
                links: 
                algorithm: The digest algorithm which is used for the fingerprint computation
                data_fingerprint: The digest value of data of the file. The fingerprint is base64 encoded. This field is not included if the scope is metadata-only.
                file_size: The size of the file in bytes.
                file_type: The type of the file.
                id: A unique identifier for the fingerprint operation
                metadata_fingerprint: The digest value of metadata of the file. The metadata fingerprint is calculated for file size, file ctime, file mtime, file crtime, file retention time, file uid, file gid, and file type. The fingerprint is base64 encoded. This field is not included if the scope is data-only.
                path: Specifies the path on which file fingerprint operation is running or has completed. Specifies the path relative to the output volume root, of the form \"/path\". The path can be path to a file or a directory.
                scope: The scope of the file which is used for the fingerprint computation
                state: Specifies the status of fingerprint operation.
                svm: 
                volume: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if algorithm is not None:
                kwargs["algorithm"] = algorithm
            if data_fingerprint is not None:
                kwargs["data_fingerprint"] = data_fingerprint
            if file_size is not None:
                kwargs["file_size"] = file_size
            if file_type is not None:
                kwargs["file_type"] = file_type
            if id is not None:
                kwargs["id"] = id
            if metadata_fingerprint is not None:
                kwargs["metadata_fingerprint"] = metadata_fingerprint
            if path is not None:
                kwargs["path"] = path
            if scope is not None:
                kwargs["scope"] = scope
            if state is not None:
                kwargs["state"] = state
            if svm is not None:
                kwargs["svm"] = svm
            if volume is not None:
                kwargs["volume"] = volume

            resource = SnaplockFileFingerprint(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SnaplockFileFingerprint: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Aborts an in-progress fingerprint operation. This API takes session-id as input and aborts the fingerprint operation that is associated with the specified session-id.
### Related ONTAP commands
* `volume file fingerprint abort`
### Learn more
* [`DOC /storage/snaplock/file-fingerprints`](#docs-snaplock-storage_snaplock_file-fingerprints)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock file fingerprint delete")
        async def snaplock_file_fingerprint_delete(
        ) -> None:
            """Delete an instance of a SnaplockFileFingerprint resource

            Args:
                algorithm: The digest algorithm which is used for the fingerprint computation
                data_fingerprint: The digest value of data of the file. The fingerprint is base64 encoded. This field is not included if the scope is metadata-only.
                file_size: The size of the file in bytes.
                file_type: The type of the file.
                id: A unique identifier for the fingerprint operation
                metadata_fingerprint: The digest value of metadata of the file. The metadata fingerprint is calculated for file size, file ctime, file mtime, file crtime, file retention time, file uid, file gid, and file type. The fingerprint is base64 encoded. This field is not included if the scope is data-only.
                path: Specifies the path on which file fingerprint operation is running or has completed. Specifies the path relative to the output volume root, of the form \"/path\". The path can be path to a file or a directory.
                scope: The scope of the file which is used for the fingerprint computation
                state: Specifies the status of fingerprint operation.
            """

            kwargs = {}
            if algorithm is not None:
                kwargs["algorithm"] = algorithm
            if data_fingerprint is not None:
                kwargs["data_fingerprint"] = data_fingerprint
            if file_size is not None:
                kwargs["file_size"] = file_size
            if file_type is not None:
                kwargs["file_type"] = file_type
            if id is not None:
                kwargs["id"] = id
            if metadata_fingerprint is not None:
                kwargs["metadata_fingerprint"] = metadata_fingerprint
            if path is not None:
                kwargs["path"] = path
            if scope is not None:
                kwargs["scope"] = scope
            if state is not None:
                kwargs["state"] = state

            if hasattr(SnaplockFileFingerprint, "find"):
                resource = SnaplockFileFingerprint.find(
                    **kwargs
                )
            else:
                resource = SnaplockFileFingerprint()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete SnaplockFileFingerprint: %s" % err)


