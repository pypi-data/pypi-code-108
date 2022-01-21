r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
A LUN map's reporting nodes are the cluster nodes from which network paths to a mapped LUN are advertised via the SAN protocols as part of the Selective LUN Map (SLM) feature of ONTAP. SLM reduces the number of paths from the host to a mapped LUN and enables management of a single initiator group (igroup) per host.<br/>
If there are no reporting nodes in a LUN map, network paths to all cluster nodes having the appropriate network interfaces (LIFs) in the SVM are advertised. This is not a typical configuration and is reserved for limited specific use cases. Note that having no reporting nodes in a LUN map differs subtly from having all reporting nodes in the LUN map. If a LUN map has an empty reporting nodes list and a new node is added to the cluster, a path to the new node will also be advertised. If a LUN map has all cluster nodes in its reporting nodes list and a new node is added to the cluster, a path to the new node is not advertised unless the LUN map's reporting nodes are explicitly updated to include the new node.<br/>
If portsets are used to further restrict access for initiators to specific LIFs, the mapped LUN will be accessible only via the LIFs in the portset that are on the reporting nodes of the LUN map.<br/>
When a LUN map is created, the cluster node hosting the mapped LUN and its high availability (HA) partner are set as the initial reporting nodes.<br/>
Before moving a mapped LUN or a volume containing mapped LUNs to another HA pair within the same cluster, the destination node should be added to the LUN map's reporting nodes. This ensures that active, optimized LUN paths are maintained. After moving a mapped LUN or a volume containing mapped LUNs to another HA pair within the same cluster, the cluster node that previously hosted the mapped LUN should be removed from the LUN map's reporting node. Further details for this workflow may be found in the ONTAP SAN Administration documentation - see `Modifying the SLM reporting-nodes list`.<br/>
The LUN map reporting nodes REST API allows you to add, remove and discover the reporting nodes of a LUN map.
## Examples
### Adding a node to a LUN map
This example adds a cluster node, and its high availability (HA) partner cluster node, to a LUN map's reporting nodes.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LunMapReportingNode

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LunMapReportingNode("b10a8165-8346-11eb-ab8e-005056bbb402")
    resource.name = "node2"
    resource.post(hydrate=True)
    print(resource)

```

---
### Removing a node from a LUN map
This example removes a cluster node, and its high availability (HA) partner cluster node, from a LUN map's reporting nodes.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LunMapReportingNode

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LunMapReportingNode(
        "b10a8165-8346-11eb-ab8e-005056bbb402",
        uuid="6d2cd7d5-493a-daf8-9ae1-219e4ad6f77d",
    )
    resource.delete()

```

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


__all__ = ["LunMapReportingNode", "LunMapReportingNodeSchema"]
__pdoc__ = {
    "LunMapReportingNodeSchema.resource": False,
    "LunMapReportingNode.lun_map_reporting_node_show": False,
    "LunMapReportingNode.lun_map_reporting_node_create": False,
    "LunMapReportingNode.lun_map_reporting_node_modify": False,
    "LunMapReportingNode.lun_map_reporting_node_delete": False,
}


class LunMapReportingNodeSchema(ResourceSchema):
    """The fields of the LunMapReportingNode object"""

    links = fields.Nested("netapp_ontap.models.lun_map_reporting_node_links.LunMapReportingNodeLinksSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the lun_map_reporting_node. """

    igroup = fields.Nested("netapp_ontap.models.lun_map_reporting_node_igroup.LunMapReportingNodeIgroupSchema", data_key="igroup", unknown=EXCLUDE)
    r""" The igroup field of the lun_map_reporting_node. """

    lun = fields.Nested("netapp_ontap.models.lun_map_reporting_node_lun.LunMapReportingNodeLunSchema", data_key="lun", unknown=EXCLUDE)
    r""" The lun field of the lun_map_reporting_node. """

    name = fields.Str(
        data_key="name",
    )
    r""" The name of the node.<br/>
Either `uuid` or `name` are required in POST.


Example: node1 """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The unique identifier of the node.<br/>
Either `uuid` or `name` are required in POST.


Example: 5ac8eb9c-4e32-dbaa-57ca-fb905976f54e """

    @property
    def resource(self):
        return LunMapReportingNode

    gettable_fields = [
        "links",
        "igroup",
        "lun",
        "name",
        "uuid",
    ]
    """links,igroup,lun,name,uuid,"""

    patchable_fields = [
        "igroup",
        "lun",
    ]
    """igroup,lun,"""

    postable_fields = [
        "igroup",
        "lun",
        "name",
        "uuid",
    ]
    """igroup,lun,name,uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in LunMapReportingNode.get_collection(fields=field)]
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
            raise NetAppRestError("LunMapReportingNode modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class LunMapReportingNode(Resource):
    r""" A cluster node from which network paths to the LUN are advertised by ONTAP via the SAN protocols. """

    _schema = LunMapReportingNodeSchema
    _path = "/api/protocols/san/lun-maps/{lun[uuid]}/{igroup[uuid]}/reporting-nodes"
    _keys = ["lun.uuid", "igroup.uuid", "uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves LUN map reporting nodes.
### Related ONTAP commands
* `lun mapping show`
### Learn more
* [`DOC /protocols/san/lun-maps/{lun.uuid}/{igroup.uuid}/reporting-nodes`](#docs-SAN-protocols_san_lun-maps_{lun.uuid}_{igroup.uuid}_reporting-nodes)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="lun map reporting node show")
        def lun_map_reporting_node_show(
            igroup_uuid,
            lun_uuid,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            uuid: Choices.define(_get_field_list("uuid"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["name", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of LunMapReportingNode resources

            Args:
                name: The name of the node.<br/> Either `uuid` or `name` are required in POST. 
                uuid: The unique identifier of the node.<br/> Either `uuid` or `name` are required in POST. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return LunMapReportingNode.get_collection(
                igroup_uuid,
                lun_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all LunMapReportingNode resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["LunMapReportingNode"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["LunMapReportingNode"], NetAppResponse]:
        r"""Adds a reporting node and its HA partner to a LUN map.
### Required properties
* `node.uuid` or `node.name` - A cluster node to add.
### Related ONTAP commands
* `lun mapping add-reporting-nodes`
### Learn more
* [`DOC /protocols/san/lun-maps/{lun.uuid}/{igroup.uuid}/reporting-nodes`](#docs-SAN-protocols_san_lun-maps_{lun.uuid}_{igroup.uuid}_reporting-nodes)
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
        records: Iterable["LunMapReportingNode"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Removes a reporting node and its HA partner from a LUN map.
### Related ONTAP commands
* `lun mapping remove-reporting-nodes`
### Learn more
* [`DOC /protocols/san/lun-maps/{lun.uuid}/{igroup.uuid}/reporting-nodes`](#docs-SAN-protocols_san_lun-maps_{lun.uuid}_{igroup.uuid}_reporting-nodes)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves LUN map reporting nodes.
### Related ONTAP commands
* `lun mapping show`
### Learn more
* [`DOC /protocols/san/lun-maps/{lun.uuid}/{igroup.uuid}/reporting-nodes`](#docs-SAN-protocols_san_lun-maps_{lun.uuid}_{igroup.uuid}_reporting-nodes)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a LUN map reporting node.
### Related ONTAP commands
* `lun mapping show`
### Learn more
* [`DOC /protocols/san/lun-maps/{lun.uuid}/{igroup.uuid}/reporting-nodes`](#docs-SAN-protocols_san_lun-maps_{lun.uuid}_{igroup.uuid}_reporting-nodes)
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
        r"""Adds a reporting node and its HA partner to a LUN map.
### Required properties
* `node.uuid` or `node.name` - A cluster node to add.
### Related ONTAP commands
* `lun mapping add-reporting-nodes`
### Learn more
* [`DOC /protocols/san/lun-maps/{lun.uuid}/{igroup.uuid}/reporting-nodes`](#docs-SAN-protocols_san_lun-maps_{lun.uuid}_{igroup.uuid}_reporting-nodes)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="lun map reporting node create")
        async def lun_map_reporting_node_create(
            igroup_uuid,
            lun_uuid,
            links: dict = None,
            igroup: dict = None,
            lun: dict = None,
            name: str = None,
            uuid: str = None,
        ) -> ResourceTable:
            """Create an instance of a LunMapReportingNode resource

            Args:
                links: 
                igroup: 
                lun: 
                name: The name of the node.<br/> Either `uuid` or `name` are required in POST. 
                uuid: The unique identifier of the node.<br/> Either `uuid` or `name` are required in POST. 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if igroup is not None:
                kwargs["igroup"] = igroup
            if lun is not None:
                kwargs["lun"] = lun
            if name is not None:
                kwargs["name"] = name
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = LunMapReportingNode(
                igroup_uuid,
                lun_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create LunMapReportingNode: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Removes a reporting node and its HA partner from a LUN map.
### Related ONTAP commands
* `lun mapping remove-reporting-nodes`
### Learn more
* [`DOC /protocols/san/lun-maps/{lun.uuid}/{igroup.uuid}/reporting-nodes`](#docs-SAN-protocols_san_lun-maps_{lun.uuid}_{igroup.uuid}_reporting-nodes)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="lun map reporting node delete")
        async def lun_map_reporting_node_delete(
            igroup_uuid,
            lun_uuid,
            name: str = None,
            uuid: str = None,
        ) -> None:
            """Delete an instance of a LunMapReportingNode resource

            Args:
                name: The name of the node.<br/> Either `uuid` or `name` are required in POST. 
                uuid: The unique identifier of the node.<br/> Either `uuid` or `name` are required in POST. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(LunMapReportingNode, "find"):
                resource = LunMapReportingNode.find(
                    igroup_uuid,
                    lun_uuid,
                    **kwargs
                )
            else:
                resource = LunMapReportingNode(igroup_uuid,lun_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete LunMapReportingNode: %s" % err)


