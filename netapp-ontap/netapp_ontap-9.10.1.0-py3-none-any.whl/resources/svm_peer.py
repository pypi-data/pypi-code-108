r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Managing SVM peers
The SVM peer commands allow you to create and manage SVM peering relationships.
### SVM peer APIs
The following APIs are used to manage SVM peers:
- GET /api/svm/peers
- POST /api/svm/peers
- GET /api/svm/peers/{uuid}
- PATCH /api/svm/peers/{uuid}
- DELETE /api/svm/peers/{uuid}
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


__all__ = ["SvmPeer", "SvmPeerSchema"]
__pdoc__ = {
    "SvmPeerSchema.resource": False,
    "SvmPeer.svm_peer_show": False,
    "SvmPeer.svm_peer_create": False,
    "SvmPeer.svm_peer_modify": False,
    "SvmPeer.svm_peer_delete": False,
}


class SvmPeerSchema(ResourceSchema):
    """The fields of the SvmPeer object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the svm_peer. """

    applications = fields.List(fields.Str, data_key="applications")
    r""" A list of applications for an SVM peer relation.

Example: ["snapmirror","lun_copy"] """

    name = fields.Str(
        data_key="name",
    )
    r""" A peer SVM alias name to avoid a name conflict on the local cluster. """

    peer = fields.Nested("netapp_ontap.models.peer.PeerSchema", data_key="peer", unknown=EXCLUDE)
    r""" The peer field of the svm_peer. """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['peered', 'rejected', 'suspended', 'initiated', 'pending', 'initializing']),
    )
    r""" SVM peering state. To accept a pending SVM peer request, PATCH the state to "peered". To reject a pending SVM peer request, PATCH the state to "rejected". To suspend a peered SVM peer relation, PATCH the state to "suspended". To resume a suspended SVM peer relation, PATCH the state to "peered". The states "initiated", "pending", and "initializing" are system-generated and cannot be used for PATCH.

Valid choices:

* peered
* rejected
* suspended
* initiated
* pending
* initializing """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the svm_peer. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" SVM peer relation UUID """

    @property
    def resource(self):
        return SvmPeer

    gettable_fields = [
        "links",
        "applications",
        "name",
        "peer.cluster",
        "peer.svm",
        "state",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
    ]
    """links,applications,name,peer.cluster,peer.svm,state,svm.links,svm.name,svm.uuid,uuid,"""

    patchable_fields = [
        "applications",
        "state",
    ]
    """applications,state,"""

    postable_fields = [
        "applications",
        "name",
        "peer.cluster",
        "peer.svm",
        "svm.name",
        "svm.uuid",
    ]
    """applications,name,peer.cluster,peer.svm,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SvmPeer.get_collection(fields=field)]
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
            raise NetAppRestError("SvmPeer modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SvmPeer(Resource):
    r""" An SVM peer relation object. """

    _schema = SvmPeerSchema
    _path = "/api/svm/peers"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the list of SVM peer relationships.
### Related ONTAP commands
* `vserver peer show`
### Examples
The following examples show how to retrieve a collection of SVM peer relationships based on a query.
1. Retrieves a list of SVM peers of a specific local SVM
   <br/>
   ```
   GET "/api/svm/peers/?svm.name=VS1"
   ```
   <br/>
2. Retrieves a list of SVM peers of a specific cluster peer
   <br/>
   ```
   GET "/api/svm/peers/?peer.cluster.name=cluster2"
   ```
   <br/>
### Learn more
* [`DOC /svm/peers`](#docs-svm-svm_peers)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="svm peer show")
        def svm_peer_show(
            fields: List[Choices.define(["applications", "name", "state", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SvmPeer resources

            Args:
                applications: A list of applications for an SVM peer relation.
                name: A peer SVM alias name to avoid a name conflict on the local cluster.
                state: SVM peering state. To accept a pending SVM peer request, PATCH the state to \"peered\". To reject a pending SVM peer request, PATCH the state to \"rejected\". To suspend a peered SVM peer relation, PATCH the state to \"suspended\". To resume a suspended SVM peer relation, PATCH the state to \"peered\". The states \"initiated\", \"pending\", and \"initializing\" are system-generated and cannot be used for PATCH.
                uuid: SVM peer relation UUID
            """

            kwargs = {}
            if applications is not None:
                kwargs["applications"] = applications
            if name is not None:
                kwargs["name"] = name
            if state is not None:
                kwargs["state"] = state
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SvmPeer.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SvmPeer resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["SvmPeer"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the SVM peer relationship.
### Related ONTAP commands
* `vserver peer modify`
### Examples
The following examples show how to update an SVM peer relationship. The input parameter 'name' refers to the local name of the peer SVM.
<br/>
1. Accepts an SVM peer relationship
   <br/>
   ```
   PATCH "/api/svm/peers/d3268a74-ee76-11e8-a9bb-005056ac6dc9" '{"state":"peered"}'
   ```
   <br/>
2. Updates the local name of an SVM peer relationship
   <br/>
   ```
   PATCH "/api/svm/peers/d3268a74-ee76-11e8-a9bb-005056ac6dc9" '{"name":"vs2"}'
   ```
   <br/>
### Learn more
* [`DOC /svm/peers`](#docs-svm-svm_peers)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["SvmPeer"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["SvmPeer"], NetAppResponse]:
        r"""Creates a new SVM peer relationship.
### Important notes
  * The create request accepts peer SVM name as input instead of peer SVM UUID as the local cluster cannot validate peer SVM based on UUID.
  * The input parameter `name` refers to the local name of the peer SVM. The `peer cluster name` parameter is optional for creating intracluster SVM peer relationships.
### Required properties
* `svm.name` or `svm.uuid` - SVM name or SVM UUID
* `peer.svm.name` or `peer.svm.uuid` - Peer SVM name or Peer SVM UUID
* `peer.cluster.name` or `peer.cluster.uuid` - Peer cluster name or peer cluster UUID
* `applications` - Peering applications
### Related ONTAP commands
* `vserver peer create`
### Example
Creates a new SVM peer relationship.
<br/>
```
POST "/api/svm/peers" '{"svm":{"name":"vs1"}, "peer.cluster.name":"cluster2", "peer.svm.name":"VS1", "applications":["snapmirror"]}'
```
<br/>
### Learn more
* [`DOC /svm/peers`](#docs-svm-svm_peers)
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
        records: Iterable["SvmPeer"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the SVM peer relationship.
### Related ONTAP commands
* `vserver peer delete`
### Example
Deletes an SVM peer relationship.
<br/>
```
DELETE "/api/svm/peers/d3268a74-ee76-11e8-a9bb-005056ac6dc9"
```
<br/>
### Learn more
* [`DOC /svm/peers`](#docs-svm-svm_peers)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the list of SVM peer relationships.
### Related ONTAP commands
* `vserver peer show`
### Examples
The following examples show how to retrieve a collection of SVM peer relationships based on a query.
1. Retrieves a list of SVM peers of a specific local SVM
   <br/>
   ```
   GET "/api/svm/peers/?svm.name=VS1"
   ```
   <br/>
2. Retrieves a list of SVM peers of a specific cluster peer
   <br/>
   ```
   GET "/api/svm/peers/?peer.cluster.name=cluster2"
   ```
   <br/>
### Learn more
* [`DOC /svm/peers`](#docs-svm-svm_peers)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the SVM peer relationship instance.
### Related ONTAP commands
* `vserver peer show`
### Example
Retrieves the parameters of an SVM peer relationship.
<br/>
```
GET "/api/svm/peers/d3268a74-ee76-11e8-a9bb-005056ac6dc9"
```
<br/>
### Learn more
* [`DOC /svm/peers`](#docs-svm-svm_peers)
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
        r"""Creates a new SVM peer relationship.
### Important notes
  * The create request accepts peer SVM name as input instead of peer SVM UUID as the local cluster cannot validate peer SVM based on UUID.
  * The input parameter `name` refers to the local name of the peer SVM. The `peer cluster name` parameter is optional for creating intracluster SVM peer relationships.
### Required properties
* `svm.name` or `svm.uuid` - SVM name or SVM UUID
* `peer.svm.name` or `peer.svm.uuid` - Peer SVM name or Peer SVM UUID
* `peer.cluster.name` or `peer.cluster.uuid` - Peer cluster name or peer cluster UUID
* `applications` - Peering applications
### Related ONTAP commands
* `vserver peer create`
### Example
Creates a new SVM peer relationship.
<br/>
```
POST "/api/svm/peers" '{"svm":{"name":"vs1"}, "peer.cluster.name":"cluster2", "peer.svm.name":"VS1", "applications":["snapmirror"]}'
```
<br/>
### Learn more
* [`DOC /svm/peers`](#docs-svm-svm_peers)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="svm peer create")
        async def svm_peer_create(
        ) -> ResourceTable:
            """Create an instance of a SvmPeer resource

            Args:
                links: 
                applications: A list of applications for an SVM peer relation.
                name: A peer SVM alias name to avoid a name conflict on the local cluster.
                peer: 
                state: SVM peering state. To accept a pending SVM peer request, PATCH the state to \"peered\". To reject a pending SVM peer request, PATCH the state to \"rejected\". To suspend a peered SVM peer relation, PATCH the state to \"suspended\". To resume a suspended SVM peer relation, PATCH the state to \"peered\". The states \"initiated\", \"pending\", and \"initializing\" are system-generated and cannot be used for PATCH.
                svm: 
                uuid: SVM peer relation UUID
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if applications is not None:
                kwargs["applications"] = applications
            if name is not None:
                kwargs["name"] = name
            if peer is not None:
                kwargs["peer"] = peer
            if state is not None:
                kwargs["state"] = state
            if svm is not None:
                kwargs["svm"] = svm
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = SvmPeer(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SvmPeer: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the SVM peer relationship.
### Related ONTAP commands
* `vserver peer modify`
### Examples
The following examples show how to update an SVM peer relationship. The input parameter 'name' refers to the local name of the peer SVM.
<br/>
1. Accepts an SVM peer relationship
   <br/>
   ```
   PATCH "/api/svm/peers/d3268a74-ee76-11e8-a9bb-005056ac6dc9" '{"state":"peered"}'
   ```
   <br/>
2. Updates the local name of an SVM peer relationship
   <br/>
   ```
   PATCH "/api/svm/peers/d3268a74-ee76-11e8-a9bb-005056ac6dc9" '{"name":"vs2"}'
   ```
   <br/>
### Learn more
* [`DOC /svm/peers`](#docs-svm-svm_peers)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="svm peer modify")
        async def svm_peer_modify(
        ) -> ResourceTable:
            """Modify an instance of a SvmPeer resource

            Args:
                applications: A list of applications for an SVM peer relation.
                query_applications: A list of applications for an SVM peer relation.
                name: A peer SVM alias name to avoid a name conflict on the local cluster.
                query_name: A peer SVM alias name to avoid a name conflict on the local cluster.
                state: SVM peering state. To accept a pending SVM peer request, PATCH the state to \"peered\". To reject a pending SVM peer request, PATCH the state to \"rejected\". To suspend a peered SVM peer relation, PATCH the state to \"suspended\". To resume a suspended SVM peer relation, PATCH the state to \"peered\". The states \"initiated\", \"pending\", and \"initializing\" are system-generated and cannot be used for PATCH.
                query_state: SVM peering state. To accept a pending SVM peer request, PATCH the state to \"peered\". To reject a pending SVM peer request, PATCH the state to \"rejected\". To suspend a peered SVM peer relation, PATCH the state to \"suspended\". To resume a suspended SVM peer relation, PATCH the state to \"peered\". The states \"initiated\", \"pending\", and \"initializing\" are system-generated and cannot be used for PATCH.
                uuid: SVM peer relation UUID
                query_uuid: SVM peer relation UUID
            """

            kwargs = {}
            changes = {}
            if query_applications is not None:
                kwargs["applications"] = query_applications
            if query_name is not None:
                kwargs["name"] = query_name
            if query_state is not None:
                kwargs["state"] = query_state
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if applications is not None:
                changes["applications"] = applications
            if name is not None:
                changes["name"] = name
            if state is not None:
                changes["state"] = state
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(SvmPeer, "find"):
                resource = SvmPeer.find(
                    **kwargs
                )
            else:
                resource = SvmPeer()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify SvmPeer: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the SVM peer relationship.
### Related ONTAP commands
* `vserver peer delete`
### Example
Deletes an SVM peer relationship.
<br/>
```
DELETE "/api/svm/peers/d3268a74-ee76-11e8-a9bb-005056ac6dc9"
```
<br/>
### Learn more
* [`DOC /svm/peers`](#docs-svm-svm_peers)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="svm peer delete")
        async def svm_peer_delete(
        ) -> None:
            """Delete an instance of a SvmPeer resource

            Args:
                applications: A list of applications for an SVM peer relation.
                name: A peer SVM alias name to avoid a name conflict on the local cluster.
                state: SVM peering state. To accept a pending SVM peer request, PATCH the state to \"peered\". To reject a pending SVM peer request, PATCH the state to \"rejected\". To suspend a peered SVM peer relation, PATCH the state to \"suspended\". To resume a suspended SVM peer relation, PATCH the state to \"peered\". The states \"initiated\", \"pending\", and \"initializing\" are system-generated and cannot be used for PATCH.
                uuid: SVM peer relation UUID
            """

            kwargs = {}
            if applications is not None:
                kwargs["applications"] = applications
            if name is not None:
                kwargs["name"] = name
            if state is not None:
                kwargs["state"] = state
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(SvmPeer, "find"):
                resource = SvmPeer.find(
                    **kwargs
                )
            else:
                resource = SvmPeer()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete SvmPeer: %s" % err)


