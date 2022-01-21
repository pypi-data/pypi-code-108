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


__all__ = ["PerformanceSvmNfs", "PerformanceSvmNfsSchema"]
__pdoc__ = {
    "PerformanceSvmNfsSchema.resource": False,
    "PerformanceSvmNfs.performance_svm_nfs_show": False,
    "PerformanceSvmNfs.performance_svm_nfs_create": False,
    "PerformanceSvmNfs.performance_svm_nfs_modify": False,
    "PerformanceSvmNfs.performance_svm_nfs_delete": False,
}


class PerformanceSvmNfsSchema(ResourceSchema):
    """The fields of the PerformanceSvmNfs object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the performance_svm_nfs. """

    @property
    def resource(self):
        return PerformanceSvmNfs

    gettable_fields = [
        "links",
    ]
    """links,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in PerformanceSvmNfs.get_collection(fields=field)]
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
            raise NetAppRestError("PerformanceSvmNfs modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class PerformanceSvmNfs(Resource):
    r""" Performance numbers, such as IOPS latency and throughput, for SVM-NFS protocol. """

    _schema = PerformanceSvmNfsSchema
    _path = "/api/protocols/nfs/services/{svm[uuid]}/metrics"
    _keys = ["svm.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves historical performance metrics for the NFS protocol of an SVM."""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="performance svm nfs show")
        def performance_svm_nfs_show(
            svm_uuid,
            fields: List[Choices.define(["*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of PerformanceSvmNfs resources

            Args:
            """

            kwargs = {}
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return PerformanceSvmNfs.get_collection(
                svm_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all PerformanceSvmNfs resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves historical performance metrics for the NFS protocol of an SVM."""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)






