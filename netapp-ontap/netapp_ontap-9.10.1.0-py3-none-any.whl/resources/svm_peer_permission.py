r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Managing SVM peer permissions
A cluster administrator can provide permissions for use during intercluster SVM peer relationship creation. Once this permission exists for a local SVM and peer cluster combination on a local cluster, no explicit SVM peer accept (or REST PATCH) API is required for any incoming SVM peer relationship creation requests from a remote cluster for that local SVM. Peer relationship directly changes the state to peered on both clusters. Use an SVM name as "*" to create permissions that apply to all local SVMs.
### SVM peer permission APIs
The following APIs are used to manage SVM peer permissions:
- GET /api/svm/peer-permissions
- POST /api/svm/peer-permissions
- GET /api/svm/peer-permissions/{cluster_peer.uuid}/{svm.uuid}
- PATCH /api/svm/peer-permissions/{cluster_peer.uuid}/{svm.uuid}
- DELETE /api/svm/peer-permissions/{cluster_peer.uuid}/{svm.uuid}
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


__all__ = ["SvmPeerPermission", "SvmPeerPermissionSchema"]
__pdoc__ = {
    "SvmPeerPermissionSchema.resource": False,
    "SvmPeerPermission.svm_peer_permission_show": False,
    "SvmPeerPermission.svm_peer_permission_create": False,
    "SvmPeerPermission.svm_peer_permission_modify": False,
    "SvmPeerPermission.svm_peer_permission_delete": False,
}


class SvmPeerPermissionSchema(ResourceSchema):
    """The fields of the SvmPeerPermission object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the svm_peer_permission. """

    applications = fields.List(fields.Str, data_key="applications")
    r""" A list of applications for an SVM peer relation.

Example: ["snapmirror","flexcache"] """

    cluster_peer = fields.Nested("netapp_ontap.resources.cluster_peer.ClusterPeerSchema", data_key="cluster_peer", unknown=EXCLUDE)
    r""" The cluster_peer field of the svm_peer_permission. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the svm_peer_permission. """

    @property
    def resource(self):
        return SvmPeerPermission

    gettable_fields = [
        "links",
        "applications",
        "cluster_peer.links",
        "cluster_peer.name",
        "cluster_peer.uuid",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,applications,cluster_peer.links,cluster_peer.name,cluster_peer.uuid,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "applications",
    ]
    """applications,"""

    postable_fields = [
        "applications",
        "cluster_peer.name",
        "cluster_peer.uuid",
        "svm.name",
        "svm.uuid",
    ]
    """applications,cluster_peer.name,cluster_peer.uuid,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SvmPeerPermission.get_collection(fields=field)]
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
            raise NetAppRestError("SvmPeerPermission modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SvmPeerPermission(Resource):
    r""" Manage SVM peer permissions. """

    _schema = SvmPeerPermissionSchema
    _path = "/api/svm/peer-permissions"
    _keys = ["cluster_peer.uuid", "svm.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the list of SVM peer permissions.
### Related ONTAP commands
* `vserver peer permission show`
### Examples
The following examples show how to retrieve a collection of SVM peer permissions based on a query.
<br/>
1. Retrieves a list of SVM peer permissions of a specific local SVM
   <br/>
   ```
   GET "/api/svm/peer-permissions/?svm.name=VS1"
   ```
   <br/>
2. Retrieves a list of SVM peer permissions of a specific cluster peer
   <br/>
   ```
   GET "/api/svm/peer-permissions/?cluster_peer.name=cluster2"
   ```
   <br/>
### Learn more
* [`DOC /svm/peer-permissions`](#docs-svm-svm_peer-permissions)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="svm peer permission show")
        def svm_peer_permission_show(
            fields: List[Choices.define(["applications", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SvmPeerPermission resources

            Args:
                applications: A list of applications for an SVM peer relation.
            """

            kwargs = {}
            if applications is not None:
                kwargs["applications"] = applications
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SvmPeerPermission.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SvmPeerPermission resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["SvmPeerPermission"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the SVM peer permissions.
### Related ONTAP commands
* `vserver peer permission modify`
### Example
Updates an SVM peer permission.
<br/>
```
PATCH "/api/svm/peer-permissions/d3268a74-ee76-11e8-a9bb-005056ac6dc9/8f467b93-f2f1-11e8-9027-005056ac81fc" '{"applications":["flexcache"]}'
```
<br/>
### Learn more
* [`DOC /svm/peer-permissions`](#docs-svm-svm_peer-permissions)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["SvmPeerPermission"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["SvmPeerPermission"], NetAppResponse]:
        r"""Creates an SVM peer permission.
### Required properties
* `svm.name` or `svm.uuid` - SVM name
* `cluster_peer.uuid` or `cluster_peer.name` - Peer cluster name or peer cluster UUID
* `applications` - Peering applications
### Related ONTAP commands
* `vserver peer permission create`
### Examples
The following examples show how to create SVM peer permissions.
<br/>
1. Creates an SVM peer permission entry with the local SVM and cluster peer names
   <br/>
   ```
   POST "/api/svm/peer-permissions" '{"cluster_peer":{"name":"cluster2"}, "svm":{"name":"VS1"}, "applications":["snapmirror"]}'
   ```
   <br/>
2. Creates an SVM peer permission entry with the local SVM and cluster peer UUID
   <br/>
   ```
   POST "/api/svm/peer-permissions" '{"cluster_peer":{"uuid":"d3268a74-ee76-11e8-a9bb-005056ac6dc9"}, "svm":{"uuid":"8f467b93-f2f1-11e8-9027-005056ac81fc"}, "applications":["snapmirror"]}'
   ```
   <br/>
3. Creates an SVM peer permission entry with all SVMs and the cluster peer name
   <br/>
   ```
   POST "/api/svm/peer-permissions" '{"cluster_peer":{"name":"cluster2"}, "svm":{"name":"*"}, "applications":["snapmirror"]}'
   ```
   <br/>
### Learn more
* [`DOC /svm/peer-permissions`](#docs-svm-svm_peer-permissions)
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
        records: Iterable["SvmPeerPermission"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the SVM peer permissions.
### Related ONTAP commands
* `verver peer permission delete`
### Example
Deletes an SVM peer permission.
<br/>
```
DELETE "/api/svm/peer-permissions/d3268a74-ee76-11e8-a9bb-005056ac6dc9/8f467b93-f2f1-11e8-9027-005056ac81fc"
```
<br/>
### Learn more
* [`DOC /svm/peer-permissions`](#docs-svm-svm_peer-permissions)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the list of SVM peer permissions.
### Related ONTAP commands
* `vserver peer permission show`
### Examples
The following examples show how to retrieve a collection of SVM peer permissions based on a query.
<br/>
1. Retrieves a list of SVM peer permissions of a specific local SVM
   <br/>
   ```
   GET "/api/svm/peer-permissions/?svm.name=VS1"
   ```
   <br/>
2. Retrieves a list of SVM peer permissions of a specific cluster peer
   <br/>
   ```
   GET "/api/svm/peer-permissions/?cluster_peer.name=cluster2"
   ```
   <br/>
### Learn more
* [`DOC /svm/peer-permissions`](#docs-svm-svm_peer-permissions)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the SVM peer permission instance.
### Related ONTAP commands
* `vserver peer permission show`
### Example
The following example shows how to retrieve the parameters for an SVM peer permission.
<br/>
```
GET "/api/svm/peer-permissions/d3268a74-ee76-11e8-a9bb-005056ac6dc9/8f467b93-f2f1-11e8-9027-005056ac81fc"
```
<br/>
### Learn more
* [`DOC /svm/peer-permissions`](#docs-svm-svm_peer-permissions)
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
        r"""Creates an SVM peer permission.
### Required properties
* `svm.name` or `svm.uuid` - SVM name
* `cluster_peer.uuid` or `cluster_peer.name` - Peer cluster name or peer cluster UUID
* `applications` - Peering applications
### Related ONTAP commands
* `vserver peer permission create`
### Examples
The following examples show how to create SVM peer permissions.
<br/>
1. Creates an SVM peer permission entry with the local SVM and cluster peer names
   <br/>
   ```
   POST "/api/svm/peer-permissions" '{"cluster_peer":{"name":"cluster2"}, "svm":{"name":"VS1"}, "applications":["snapmirror"]}'
   ```
   <br/>
2. Creates an SVM peer permission entry with the local SVM and cluster peer UUID
   <br/>
   ```
   POST "/api/svm/peer-permissions" '{"cluster_peer":{"uuid":"d3268a74-ee76-11e8-a9bb-005056ac6dc9"}, "svm":{"uuid":"8f467b93-f2f1-11e8-9027-005056ac81fc"}, "applications":["snapmirror"]}'
   ```
   <br/>
3. Creates an SVM peer permission entry with all SVMs and the cluster peer name
   <br/>
   ```
   POST "/api/svm/peer-permissions" '{"cluster_peer":{"name":"cluster2"}, "svm":{"name":"*"}, "applications":["snapmirror"]}'
   ```
   <br/>
### Learn more
* [`DOC /svm/peer-permissions`](#docs-svm-svm_peer-permissions)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="svm peer permission create")
        async def svm_peer_permission_create(
        ) -> ResourceTable:
            """Create an instance of a SvmPeerPermission resource

            Args:
                links: 
                applications: A list of applications for an SVM peer relation.
                cluster_peer: 
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if applications is not None:
                kwargs["applications"] = applications
            if cluster_peer is not None:
                kwargs["cluster_peer"] = cluster_peer
            if svm is not None:
                kwargs["svm"] = svm

            resource = SvmPeerPermission(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SvmPeerPermission: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the SVM peer permissions.
### Related ONTAP commands
* `vserver peer permission modify`
### Example
Updates an SVM peer permission.
<br/>
```
PATCH "/api/svm/peer-permissions/d3268a74-ee76-11e8-a9bb-005056ac6dc9/8f467b93-f2f1-11e8-9027-005056ac81fc" '{"applications":["flexcache"]}'
```
<br/>
### Learn more
* [`DOC /svm/peer-permissions`](#docs-svm-svm_peer-permissions)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="svm peer permission modify")
        async def svm_peer_permission_modify(
        ) -> ResourceTable:
            """Modify an instance of a SvmPeerPermission resource

            Args:
                applications: A list of applications for an SVM peer relation.
                query_applications: A list of applications for an SVM peer relation.
            """

            kwargs = {}
            changes = {}
            if query_applications is not None:
                kwargs["applications"] = query_applications

            if applications is not None:
                changes["applications"] = applications

            if hasattr(SvmPeerPermission, "find"):
                resource = SvmPeerPermission.find(
                    **kwargs
                )
            else:
                resource = SvmPeerPermission()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify SvmPeerPermission: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the SVM peer permissions.
### Related ONTAP commands
* `verver peer permission delete`
### Example
Deletes an SVM peer permission.
<br/>
```
DELETE "/api/svm/peer-permissions/d3268a74-ee76-11e8-a9bb-005056ac6dc9/8f467b93-f2f1-11e8-9027-005056ac81fc"
```
<br/>
### Learn more
* [`DOC /svm/peer-permissions`](#docs-svm-svm_peer-permissions)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="svm peer permission delete")
        async def svm_peer_permission_delete(
        ) -> None:
            """Delete an instance of a SvmPeerPermission resource

            Args:
                applications: A list of applications for an SVM peer relation.
            """

            kwargs = {}
            if applications is not None:
                kwargs["applications"] = applications

            if hasattr(SvmPeerPermission, "find"):
                resource = SvmPeerPermission.find(
                    **kwargs
                )
            else:
                resource = SvmPeerPermission()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete SvmPeerPermission: %s" % err)


