r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

You can use this API to manage NDMP mode: SVM-scope or node-scope.
### Examples
Updates NDMP mode to SVM:
   <br/>
   ```
   PATCH "/api/protocols/ndmp" '{"mode":"svm"}'
   ```
   <br/>
Updates NDMP mode to node:
   <br/>
   ```
   PATCH "/api/protocols/ndmp" '{"mode":"node"}'
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


__all__ = ["ClusterNdmpProperties", "ClusterNdmpPropertiesSchema"]
__pdoc__ = {
    "ClusterNdmpPropertiesSchema.resource": False,
    "ClusterNdmpProperties.cluster_ndmp_properties_show": False,
    "ClusterNdmpProperties.cluster_ndmp_properties_create": False,
    "ClusterNdmpProperties.cluster_ndmp_properties_modify": False,
    "ClusterNdmpProperties.cluster_ndmp_properties_delete": False,
}


class ClusterNdmpPropertiesSchema(ResourceSchema):
    """The fields of the ClusterNdmpProperties object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the cluster_ndmp_properties. """

    mode = fields.Str(
        data_key="mode",
        validate=enum_validation(['svm', 'node']),
    )
    r""" Indicates whether NDMP is in node-scoped or SVM-scoped mode.

Valid choices:

* svm
* node """

    @property
    def resource(self):
        return ClusterNdmpProperties

    gettable_fields = [
        "links",
        "mode",
    ]
    """links,mode,"""

    patchable_fields = [
        "mode",
    ]
    """mode,"""

    postable_fields = [
        "mode",
    ]
    """mode,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in ClusterNdmpProperties.get_collection(fields=field)]
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
            raise NetAppRestError("ClusterNdmpProperties modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class ClusterNdmpProperties(Resource):
    """Allows interaction with ClusterNdmpProperties objects on the host"""

    _schema = ClusterNdmpPropertiesSchema
    _path = "/api/protocols/ndmp"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the current NDMP mode.
### Related ONTAP commands
* `system services ndmp node-scope-mode status`
### Learn more
* [`DOC /protocols/ndmp`](#docs-ndmp-protocols_ndmp)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster ndmp properties show")
        def cluster_ndmp_properties_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single ClusterNdmpProperties resource

            Args:
                mode: Indicates whether NDMP is in node-scoped or SVM-scoped mode.
            """

            kwargs = {}
            if mode is not None:
                kwargs["mode"] = mode
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = ClusterNdmpProperties(
                **kwargs
            )
            resource.get()
            return [resource]


    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the NDMP mode.
### Related ONTAP commands
* `system services ndmp node-scope-mode`
### Learn more
* [`DOC /protocols/ndmp`](#docs-ndmp-protocols_ndmp)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster ndmp properties modify")
        async def cluster_ndmp_properties_modify(
        ) -> ResourceTable:
            """Modify an instance of a ClusterNdmpProperties resource

            Args:
                mode: Indicates whether NDMP is in node-scoped or SVM-scoped mode.
                query_mode: Indicates whether NDMP is in node-scoped or SVM-scoped mode.
            """

            kwargs = {}
            changes = {}
            if query_mode is not None:
                kwargs["mode"] = query_mode

            if mode is not None:
                changes["mode"] = mode

            if hasattr(ClusterNdmpProperties, "find"):
                resource = ClusterNdmpProperties.find(
                    **kwargs
                )
            else:
                resource = ClusterNdmpProperties()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify ClusterNdmpProperties: %s" % err)



