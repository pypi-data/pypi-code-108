r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

Use this API to retain Compliance-mode WORM files for the duration of a litigation. A file under a legal-hold behaves as a WORM file with an indefinite retention period. Litigation ID is a combination of volume UUID and litigation name in the format `<volume UUID>:<litigation name>`. Only a user with the security login role vsadmin-snaplock can perform the operation.
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


__all__ = ["SnaplockLitigation", "SnaplockLitigationSchema"]
__pdoc__ = {
    "SnaplockLitigationSchema.resource": False,
    "SnaplockLitigation.snaplock_litigation_show": False,
    "SnaplockLitigation.snaplock_litigation_create": False,
    "SnaplockLitigation.snaplock_litigation_modify": False,
    "SnaplockLitigation.snaplock_litigation_delete": False,
}


class SnaplockLitigationSchema(ResourceSchema):
    """The fields of the SnaplockLitigation object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the snaplock_litigation. """

    id = fields.Str(
        data_key="id",
    )
    r""" Specifies the litigation ID. """

    name = fields.Str(
        data_key="name",
    )
    r""" Specifies the legal-hold litigation name.

Example: lit1 """

    operations = fields.List(fields.Nested("netapp_ontap.resources.snaplock_legal_hold_operation.SnaplockLegalHoldOperationSchema", unknown=EXCLUDE), data_key="operations")
    r""" The operations field of the snaplock_litigation. """

    path = fields.Str(
        data_key="path",
    )
    r""" Specifies the path on which legal-hold operation has to be applied.

Example: /dir1 """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the snaplock_litigation. """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the snaplock_litigation. """

    @property
    def resource(self):
        return SnaplockLitigation

    gettable_fields = [
        "links",
        "id",
        "name",
        "operations",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,id,name,operations,svm.links,svm.name,svm.uuid,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "name",
        "operations",
        "svm.name",
        "svm.uuid",
        "volume.name",
        "volume.uuid",
    ]
    """name,operations,svm.name,svm.uuid,volume.name,volume.uuid,"""

    postable_fields = [
        "name",
        "operations",
        "path",
        "svm.name",
        "svm.uuid",
        "volume.name",
        "volume.uuid",
    ]
    """name,operations,path,svm.name,svm.uuid,volume.name,volume.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SnaplockLitigation.get_collection(fields=field)]
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
            raise NetAppRestError("SnaplockLitigation modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SnaplockLitigation(Resource):
    """Allows interaction with SnaplockLitigation objects on the host"""

    _schema = SnaplockLitigationSchema
    _path = "/api/storage/snaplock/litigations"
    _keys = ["id"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the list of litigations under an SVM.
### Related ONTAP commands
* `snaplock legal-hold show`
### Learn more
* [`DOC /storage/snaplock/litigations`](#docs-snaplock-storage_snaplock_litigations)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock litigation show")
        def snaplock_litigation_show(
            fields: List[Choices.define(["id", "name", "path", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SnaplockLitigation resources

            Args:
                id: Specifies the litigation ID.
                name: Specifies the legal-hold litigation name.
                path: Specifies the path on which legal-hold operation has to be applied.
            """

            kwargs = {}
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if path is not None:
                kwargs["path"] = path
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SnaplockLitigation.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SnaplockLitigation resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["SnaplockLitigation"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["SnaplockLitigation"], NetAppResponse]:
        r"""Starts a  Legal-Hold.
### Required properties
* `path` - Path of the file.
* `name` - Litigation name.
* `volume.name` or `volume.uuid` - Name or UUID  of the volume.
### Related ONTAP commands
* `snaplock legal-hold begin`
### Example
<br/>
```
POST "/api/storage/snaplock/litigations" '{"volume.name":"SLC1","name":"l3","path":"/b.txt"}'
```
<br/>
### Learn more
* [`DOC /storage/snaplock/litigations`](#docs-snaplock-storage_snaplock_litigations)
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
        records: Iterable["SnaplockLitigation"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates a legal-hold end on all of the files for the specified litigation ID. This is only allowed when an operation is no longer in progress.
### Related ONTAP commands
* `snaplock legal-hold end`
### Example
<br/>
```
DELETE "/api/storage/snaplock/litigations/fd72e138-4bc3-11e9-a85f-0050568eb48f%3Al3"
```
<br/>
### Learn more
* [`DOC /storage/snaplock/litigations`](#docs-snaplock-storage_snaplock_litigations)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the list of litigations under an SVM.
### Related ONTAP commands
* `snaplock legal-hold show`
### Learn more
* [`DOC /storage/snaplock/litigations`](#docs-snaplock-storage_snaplock_litigations)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the list of ongoing operations for the specified litigation ID.
### Related ONTAP commands
* `snaplock legal-hold show`
### Learn more
* [`DOC /storage/snaplock/litigations`](#docs-snaplock-storage_snaplock_litigations)
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
        r"""Starts a  Legal-Hold.
### Required properties
* `path` - Path of the file.
* `name` - Litigation name.
* `volume.name` or `volume.uuid` - Name or UUID  of the volume.
### Related ONTAP commands
* `snaplock legal-hold begin`
### Example
<br/>
```
POST "/api/storage/snaplock/litigations" '{"volume.name":"SLC1","name":"l3","path":"/b.txt"}'
```
<br/>
### Learn more
* [`DOC /storage/snaplock/litigations`](#docs-snaplock-storage_snaplock_litigations)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock litigation create")
        async def snaplock_litigation_create(
        ) -> ResourceTable:
            """Create an instance of a SnaplockLitigation resource

            Args:
                links: 
                id: Specifies the litigation ID.
                name: Specifies the legal-hold litigation name.
                operations: 
                path: Specifies the path on which legal-hold operation has to be applied.
                svm: 
                volume: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if operations is not None:
                kwargs["operations"] = operations
            if path is not None:
                kwargs["path"] = path
            if svm is not None:
                kwargs["svm"] = svm
            if volume is not None:
                kwargs["volume"] = volume

            resource = SnaplockLitigation(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SnaplockLitigation: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates a legal-hold end on all of the files for the specified litigation ID. This is only allowed when an operation is no longer in progress.
### Related ONTAP commands
* `snaplock legal-hold end`
### Example
<br/>
```
DELETE "/api/storage/snaplock/litigations/fd72e138-4bc3-11e9-a85f-0050568eb48f%3Al3"
```
<br/>
### Learn more
* [`DOC /storage/snaplock/litigations`](#docs-snaplock-storage_snaplock_litigations)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock litigation delete")
        async def snaplock_litigation_delete(
        ) -> None:
            """Delete an instance of a SnaplockLitigation resource

            Args:
                id: Specifies the litigation ID.
                name: Specifies the legal-hold litigation name.
                path: Specifies the path on which legal-hold operation has to be applied.
            """

            kwargs = {}
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if path is not None:
                kwargs["path"] = path

            if hasattr(SnaplockLitigation, "find"):
                resource = SnaplockLitigation.find(
                    **kwargs
                )
            else:
                resource = SnaplockLitigation()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete SnaplockLitigation: %s" % err)


