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


__all__ = ["SoftwarePackage", "SoftwarePackageSchema"]
__pdoc__ = {
    "SoftwarePackageSchema.resource": False,
    "SoftwarePackage.software_package_show": False,
    "SoftwarePackage.software_package_create": False,
    "SoftwarePackage.software_package_modify": False,
    "SoftwarePackage.software_package_delete": False,
}


class SoftwarePackageSchema(ResourceSchema):
    """The fields of the SoftwarePackage object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the software_package. """

    create_time = ImpreciseDateTime(
        data_key="create_time",
    )
    r""" Indicates when this package was loaded

Example: 2019-02-04T19:00:00.000+0000 """

    version = fields.Str(
        data_key="version",
    )
    r""" Version of this package

Example: ONTAP_X """

    @property
    def resource(self):
        return SoftwarePackage

    gettable_fields = [
        "links",
        "create_time",
        "version",
    ]
    """links,create_time,version,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SoftwarePackage.get_collection(fields=field)]
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
            raise NetAppRestError("SoftwarePackage modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SoftwarePackage(Resource):
    """Allows interaction with SoftwarePackage objects on the host"""

    _schema = SoftwarePackageSchema
    _path = "/api/cluster/software/packages"
    _keys = ["version"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the software packages for a cluster.
### Related ONTAP commands
* `cluster image package show-repository`
### Learn more
* [`DOC /cluster/software`](#docs-cluster-cluster_software)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="software package show")
        def software_package_show(
            fields: List[Choices.define(["create_time", "version", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SoftwarePackage resources

            Args:
                create_time: Indicates when this package was loaded
                version: Version of this package
            """

            kwargs = {}
            if create_time is not None:
                kwargs["create_time"] = create_time
            if version is not None:
                kwargs["version"] = version
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SoftwarePackage.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SoftwarePackage resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)



    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["SoftwarePackage"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a software package from the cluster. The delete operation fails if the package is currently installed.
### Related ONTAP commands
* `cluster image package delete`
### Learn more
* [`DOC /cluster/software`](#docs-cluster-cluster_software)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the software packages for a cluster.
### Related ONTAP commands
* `cluster image package show-repository`
### Learn more
* [`DOC /cluster/software`](#docs-cluster-cluster_software)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the software package information.
### Related ONTAP commands
* `cluster image package show-repository`
### Learn more
* [`DOC /cluster/software`](#docs-cluster-cluster_software)
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
        r"""Deletes a software package from the cluster. The delete operation fails if the package is currently installed.
### Related ONTAP commands
* `cluster image package delete`
### Learn more
* [`DOC /cluster/software`](#docs-cluster-cluster_software)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="software package delete")
        async def software_package_delete(
        ) -> None:
            """Delete an instance of a SoftwarePackage resource

            Args:
                create_time: Indicates when this package was loaded
                version: Version of this package
            """

            kwargs = {}
            if create_time is not None:
                kwargs["create_time"] = create_time
            if version is not None:
                kwargs["version"] = version

            if hasattr(SoftwarePackage, "find"):
                resource = SoftwarePackage.find(
                    **kwargs
                )
            else:
                resource = SoftwarePackage()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete SoftwarePackage: %s" % err)


