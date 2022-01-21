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


__all__ = ["SoftwarePackageDownload", "SoftwarePackageDownloadSchema"]
__pdoc__ = {
    "SoftwarePackageDownloadSchema.resource": False,
    "SoftwarePackageDownload.software_package_download_show": False,
    "SoftwarePackageDownload.software_package_download_create": False,
    "SoftwarePackageDownload.software_package_download_modify": False,
    "SoftwarePackageDownload.software_package_download_delete": False,
}


class SoftwarePackageDownloadSchema(ResourceSchema):
    """The fields of the SoftwarePackageDownload object"""

    password = fields.Str(
        data_key="password",
    )
    r""" Password for download

Example: admin_password """

    url = fields.Str(
        data_key="url",
    )
    r""" HTTP or FTP URL of the package through a server

Example: http://server/package """

    username = fields.Str(
        data_key="username",
    )
    r""" Username for download

Example: admin """

    @property
    def resource(self):
        return SoftwarePackageDownload

    gettable_fields = [
    ]
    """"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "password",
        "url",
        "username",
    ]
    """password,url,username,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SoftwarePackageDownload.get_collection(fields=field)]
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
            raise NetAppRestError("SoftwarePackageDownload modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SoftwarePackageDownload(Resource):
    """Allows interaction with SoftwarePackageDownload objects on the host"""

    _schema = SoftwarePackageDownloadSchema
    _path = "/api/cluster/software/download"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the software or firmware download status.
### Related ONTAP commands
* `cluster image package check-download-progress`
### Learn more
* [`DOC /cluster/software`](#docs-cluster-cluster_software)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="software package download show")
        def software_package_download_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single SoftwarePackageDownload resource

            Args:
                password: Password for download
                url: HTTP or FTP URL of the package through a server
                username: Username for download
            """

            kwargs = {}
            if password is not None:
                kwargs["password"] = password
            if url is not None:
                kwargs["url"] = url
            if username is not None:
                kwargs["username"] = username
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = SoftwarePackageDownload(
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
        r"""Downloads a software or firmware package from the server.
### Required properties
* `url` - URL location of the software package
### Recommended optional parameters
* `username` - Username of HTTPS/FTP server
* `password` - Password of HTTPS/FTP server
### Related ONTAP commands
* `cluster image package get`
### Learn more
* [`DOC /cluster/software`](#docs-cluster-cluster_software)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="software package download create")
        async def software_package_download_create(
        ) -> ResourceTable:
            """Create an instance of a SoftwarePackageDownload resource

            Args:
                password: Password for download
                url: HTTP or FTP URL of the package through a server
                username: Username for download
            """

            kwargs = {}
            if password is not None:
                kwargs["password"] = password
            if url is not None:
                kwargs["url"] = url
            if username is not None:
                kwargs["username"] = username

            resource = SoftwarePackageDownload(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SoftwarePackageDownload: %s" % err)
            return [resource]




