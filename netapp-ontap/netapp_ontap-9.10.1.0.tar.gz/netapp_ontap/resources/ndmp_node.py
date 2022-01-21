r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

You can use this API to manage node configurations. The authentication types "plaintext" and "plaintext_sso" are used to show that the password uses clear text. Also, they contain no differences for NDMP node scope.
### Examples
Updates "enabled" and "authentication_types" fields:
   <br/>
   ```
   PATCH "/api/protocols/ndmp/nodes/13bb2092-458b-11e9-9c06-0050568ea64e" '{"enabled":"false","authentication_types":["plaintext"]}'
   ```
   <br/>
Updates the "user" field:
   <br/>
   ```
   PATCH "/api/protocols/ndmp/nodes/13bb2092-458b-11e9-9c06-0050568ea64e" '{"user":"user22"}'
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


__all__ = ["NdmpNode", "NdmpNodeSchema"]
__pdoc__ = {
    "NdmpNodeSchema.resource": False,
    "NdmpNode.ndmp_node_show": False,
    "NdmpNode.ndmp_node_create": False,
    "NdmpNode.ndmp_node_modify": False,
    "NdmpNode.ndmp_node_delete": False,
}


class NdmpNodeSchema(ResourceSchema):
    """The fields of the NdmpNode object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the ndmp_node. """

    authentication_types = fields.List(fields.Str, data_key="authentication_types")
    r""" NDMP authentication types.

Example: ["plaintext","challenge"] """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Is the NDMP service enabled?

Example: true """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the ndmp_node. """

    password = fields.Str(
        data_key="password",
    )
    r""" NDMP password. This can only be set and cannot be read back. """

    user = fields.Str(
        data_key="user",
    )
    r""" NDMP user ID

Example: ndmp_user """

    @property
    def resource(self):
        return NdmpNode

    gettable_fields = [
        "links",
        "authentication_types",
        "enabled",
        "node.links",
        "node.name",
        "node.uuid",
        "user",
    ]
    """links,authentication_types,enabled,node.links,node.name,node.uuid,user,"""

    patchable_fields = [
        "authentication_types",
        "enabled",
        "node.name",
        "node.uuid",
        "password",
        "user",
    ]
    """authentication_types,enabled,node.name,node.uuid,password,user,"""

    postable_fields = [
        "authentication_types",
        "enabled",
        "node.name",
        "node.uuid",
        "password",
        "user",
    ]
    """authentication_types,enabled,node.name,node.uuid,password,user,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NdmpNode.get_collection(fields=field)]
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
            raise NetAppRestError("NdmpNode modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NdmpNode(Resource):
    """Allows interaction with NdmpNode objects on the host"""

    _schema = NdmpNodeSchema
    _path = "/api/protocols/ndmp/nodes"
    _keys = ["node.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves NDMP node configurations for all of the nodes.
### Related ONTAP commands
* `system services ndmp show`
### Learn more
* [`DOC /protocols/ndmp/nodes`](#docs-ndmp-protocols_ndmp_nodes)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ndmp node show")
        def ndmp_node_show(
            fields: List[Choices.define(["authentication_types", "enabled", "password", "user", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of NdmpNode resources

            Args:
                authentication_types: NDMP authentication types.
                enabled: Is the NDMP service enabled?
                password: NDMP password. This can only be set and cannot be read back.
                user: NDMP user ID
            """

            kwargs = {}
            if authentication_types is not None:
                kwargs["authentication_types"] = authentication_types
            if enabled is not None:
                kwargs["enabled"] = enabled
            if password is not None:
                kwargs["password"] = password
            if user is not None:
                kwargs["user"] = user
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return NdmpNode.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NdmpNode resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["NdmpNode"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the NDMP node configuration for a specific node.
### Related ONTAP commands
* `system services ndmp modify`
### Learn more
* [`DOC /protocols/ndmp/nodes`](#docs-ndmp-protocols_ndmp_nodes)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)



    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves NDMP node configurations for all of the nodes.
### Related ONTAP commands
* `system services ndmp show`
### Learn more
* [`DOC /protocols/ndmp/nodes`](#docs-ndmp-protocols_ndmp_nodes)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an NDMP node configuration for a specific node.
### Related ONTAP commands
* `system services ndmp show`
### Learn more
* [`DOC /protocols/ndmp/nodes`](#docs-ndmp-protocols_ndmp_nodes)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)


    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the NDMP node configuration for a specific node.
### Related ONTAP commands
* `system services ndmp modify`
### Learn more
* [`DOC /protocols/ndmp/nodes`](#docs-ndmp-protocols_ndmp_nodes)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ndmp node modify")
        async def ndmp_node_modify(
        ) -> ResourceTable:
            """Modify an instance of a NdmpNode resource

            Args:
                authentication_types: NDMP authentication types.
                query_authentication_types: NDMP authentication types.
                enabled: Is the NDMP service enabled?
                query_enabled: Is the NDMP service enabled?
                password: NDMP password. This can only be set and cannot be read back.
                query_password: NDMP password. This can only be set and cannot be read back.
                user: NDMP user ID
                query_user: NDMP user ID
            """

            kwargs = {}
            changes = {}
            if query_authentication_types is not None:
                kwargs["authentication_types"] = query_authentication_types
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_password is not None:
                kwargs["password"] = query_password
            if query_user is not None:
                kwargs["user"] = query_user

            if authentication_types is not None:
                changes["authentication_types"] = authentication_types
            if enabled is not None:
                changes["enabled"] = enabled
            if password is not None:
                changes["password"] = password
            if user is not None:
                changes["user"] = user

            if hasattr(NdmpNode, "find"):
                resource = NdmpNode.find(
                    **kwargs
                )
            else:
                resource = NdmpNode()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify NdmpNode: %s" % err)



