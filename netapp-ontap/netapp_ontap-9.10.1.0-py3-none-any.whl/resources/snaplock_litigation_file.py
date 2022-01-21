r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

Displays the list of files under the specified litigation ID.
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


__all__ = ["SnaplockLitigationFile", "SnaplockLitigationFileSchema"]
__pdoc__ = {
    "SnaplockLitigationFileSchema.resource": False,
    "SnaplockLitigationFile.snaplock_litigation_file_show": False,
    "SnaplockLitigationFile.snaplock_litigation_file_create": False,
    "SnaplockLitigationFile.snaplock_litigation_file_modify": False,
    "SnaplockLitigationFile.snaplock_litigation_file_delete": False,
}


class SnaplockLitigationFileSchema(ResourceSchema):
    """The fields of the SnaplockLitigationFile object"""

    file = fields.List(fields.Str, data_key="file")
    r""" Name of the file including the path from the root. """

    sequence_index = Size(
        data_key="sequence_index",
    )
    r""" Sequence index of files path list. """

    @property
    def resource(self):
        return SnaplockLitigationFile

    gettable_fields = [
        "file",
        "sequence_index",
    ]
    """file,sequence_index,"""

    patchable_fields = [
        "file",
        "sequence_index",
    ]
    """file,sequence_index,"""

    postable_fields = [
        "file",
        "sequence_index",
    ]
    """file,sequence_index,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SnaplockLitigationFile.get_collection(fields=field)]
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
            raise NetAppRestError("SnaplockLitigationFile modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SnaplockLitigationFile(Resource):
    """Allows interaction with SnaplockLitigationFile objects on the host"""

    _schema = SnaplockLitigationFileSchema
    _path = "/api/storage/snaplock/litigations/{litigation[id]}/files"
    _keys = ["litigation.id"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Displays the list of files for the specified litigation ID.
### Learn more
* [`DOC /storage/snaplock/litigations/{litigation.id}/files`](#docs-snaplock-storage_snaplock_litigations_{litigation.id}_files)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock litigation file show")
        def snaplock_litigation_file_show(
            litigation_id,
            file: Choices.define(_get_field_list("file"), cache_choices=True, inexact=True)=None,
            sequence_index: Choices.define(_get_field_list("sequence_index"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["file", "sequence_index", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SnaplockLitigationFile resources

            Args:
                file: Name of the file including the path from the root.
                sequence_index: Sequence index of files path list.
            """

            kwargs = {}
            if file is not None:
                kwargs["file"] = file
            if sequence_index is not None:
                kwargs["sequence_index"] = sequence_index
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SnaplockLitigationFile.get_collection(
                litigation_id,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SnaplockLitigationFile resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Displays the list of files for the specified litigation ID.
### Learn more
* [`DOC /storage/snaplock/litigations/{litigation.id}/files`](#docs-snaplock-storage_snaplock_litigations_{litigation.id}_files)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)






