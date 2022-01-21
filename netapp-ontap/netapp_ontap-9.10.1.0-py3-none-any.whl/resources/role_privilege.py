r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
A role can comprise of multiple tuples and each tuple consists of the REST API path and its access level. These APIs can be used to retrieve and modify the access level or delete one of the constituent REST API paths within a role. The REST API path can be a resource-qualified endpoint. Currently, the only supported resource-qualified endpoints are <i>/api/storage/volumes/{volume.uuid}/snapshots</i> and <i>/api/storage/volumes/\*/snapshots</i>. "*" is a wildcard character denoting "all" volumes.<p/>
The role can be SVM-scoped or cluster-scoped.<p/>
Specify the owner UUID and the role name in the URI path. The owner UUID corresponds to the UUID of the SVM for which the role has been created and can be obtained from the response body of a GET request performed on one of the following APIs:
<i>/api/security/roles</i> for all roles
<i>/api/security/roles/?scope=svm</i> for SVM-scoped roles
<i>/api/security/roles/?owner.name=<svm-name></i> for roles in a specific SVM
This API response contains the complete URI for each tuple of the role and can be used for GET, PATCH, or DELETE operations.<p/>
Note: The access level for paths in pre-defined roles cannot be updated.
<br/>
## Examples
### Updating the access level for a path in the privilege tuple of an existing role
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import RolePrivilege

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = RolePrivilege("svm_role1", path="/api/protocols")
    resource.access = "all"
    resource.patch()

```

### Updating the access level for a resource-qualified endpoint in the privilege tuple of an existing role
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import RolePrivilege

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = RolePrivilege(
        "svm_role1",
        path="/api/storage/volumes/742ef001-24f0-4d5a-9ec1-2fdaadb282f4/snapshots",
    )
    resource.access = "readonly"
    resource.patch()

```

### Retrieving the access level for a path in the privilege tuple of an existing role
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import RolePrivilege

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = RolePrivilege("svm_role1", path="/api/protocols")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
RolePrivilege(
    {
        "path": "/api/protocols",
        "access": "all",
        "_links": {
            "self": {
                "href": "/api/security/roles/aaef7c38-4bd3-11e9-b238-0050568e2e25/svm_role1/privileges/%2Fapi%2Fprotocols"
            }
        },
    }
)

```
</div>
</div>

### Retrieving the access level for a resource-qualified endpoint in the privilege tuple of an existing role
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import RolePrivilege

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = RolePrivilege(
        "svm_role1",
        path="/api/storage/volumes/d0f3b91a-4ce7-4de4-afb9-7eda668659dd//snapshots",
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
RolePrivilege(
    {
        "path": "/api/storage/volumes/d0f3b91a-4ce7-4de4-afb9-7eda668659dd/snapshots",
        "access": "all",
        "_links": {
            "self": {
                "href": "/api/security/roles/aaef7c38-4bd3-11e9-b238-0050568e2e25/svm_role1/privileges/%2Fapi%2Fstorage%2Fvolumes%2Fd0f3b91a-4ce7-4de4-afb9-7eda668659dd%2Fsnapshots"
            }
        },
    }
)

```
</div>
</div>

### Deleting a privilege tuple from an existing role
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import RolePrivilege

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = RolePrivilege("svm_role1", path="/api/protocols")
    resource.delete()

```

### Deleting a privilege tuple, containing a resource-qualified endpoint, from an existing role
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import RolePrivilege

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = RolePrivilege(
        "svm_role1",
        path="/api/storage/volumes/742ef001-24f0-4d5a-9ec1-2fdaadb282f4/snapshots",
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


__all__ = ["RolePrivilege", "RolePrivilegeSchema"]
__pdoc__ = {
    "RolePrivilegeSchema.resource": False,
    "RolePrivilege.role_privilege_show": False,
    "RolePrivilege.role_privilege_create": False,
    "RolePrivilege.role_privilege_modify": False,
    "RolePrivilege.role_privilege_delete": False,
}


class RolePrivilegeSchema(ResourceSchema):
    """The fields of the RolePrivilege object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the role_privilege. """

    access = fields.Str(
        data_key="access",
    )
    r""" The access field of the role_privilege. """

    path = fields.Str(
        data_key="path",
    )
    r""" REST URI/endpoint

Example: /api/storage/volumes """

    @property
    def resource(self):
        return RolePrivilege

    gettable_fields = [
        "links",
        "access",
        "path",
    ]
    """links,access,path,"""

    patchable_fields = [
        "access",
    ]
    """access,"""

    postable_fields = [
        "access",
        "path",
    ]
    """access,path,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in RolePrivilege.get_collection(fields=field)]
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
            raise NetAppRestError("RolePrivilege modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class RolePrivilege(Resource):
    r""" A tuple containing the REST endpoint and the access level assigned to that endpoint. The REST endpoint can be a resource-qualified endpoint. At present, the only supported resource-qualified endpoints are <i>/api/storage/volumes/{volume.uuid}/snapshots</i> and <i>/api/storage/volumes/\*/snapshots</i>. "*" is a wildcard character denoting "all" volumes. """

    _schema = RolePrivilegeSchema
    _path = "/api/security/roles/{owner[uuid]}/{role[name]}/privileges"
    _keys = ["owner.uuid", "role.name", "path"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves privilege details of the specified role.
### Related ONTAP commands
* `security login rest-role show`
### Learn more
* [`DOC /security/roles/{owner.uuid}/{name}/privileges`](#docs-security-security_roles_{owner.uuid}_{name}_privileges)
* [`DOC /security/roles`](#docs-security-security_roles)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="role privilege show")
        def role_privilege_show(
            name,
            owner_uuid,
            access: Choices.define(_get_field_list("access"), cache_choices=True, inexact=True)=None,
            path: Choices.define(_get_field_list("path"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["access", "path", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of RolePrivilege resources

            Args:
                access: 
                path: REST URI/endpoint
            """

            kwargs = {}
            if access is not None:
                kwargs["access"] = access
            if path is not None:
                kwargs["path"] = path
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return RolePrivilege.get_collection(
                name,
                owner_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all RolePrivilege resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["RolePrivilege"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the privilege level for a REST API path. The REST API path can be a resource-qualified endpoint. Currently, the only supported resource-qualified endpoints are <i>/api/storage/volumes/{volume.uuid}/snapshots</i> and <i>/api/storage/volumes/\*/snapshots</i>. "*" is a wildcard character denoting "all" volumes.
### Required parameters
* `owner.uuid` - UUID of the SVM that houses this role.
* `name` - Name of the role to be updated.
* `path` - Constituent REST API path whose access level is to be updated. Can be a resource-qualified endpoint (example: <i>/api/storage/volumes/43256a71-be02-474d-a2a9-9642e12a6a2c/snapshots</i>). Currently, resource-qualified endpoints are limited to the "snapshots" endpoint: <i>/api/storage/volumes/{volume.uuid}/snapshots</i> and <i>/api/storage/volumes/\*/snapshots</i>. "*" is a wildcard character denoting "all" volumes.
* `access` - Access level for the path (one of "all", "readonly", or "none")
### Related ONTAP commands
* `security login rest-role modify`
### Learn more
* [`DOC /security/roles/{owner.uuid}/{name}/privileges/{path}`](#docs-security-security_roles_{owner.uuid}_{name}_privileges_{path})
* [`DOC /security/roles`](#docs-security-security_roles)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["RolePrivilege"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["RolePrivilege"], NetAppResponse]:
        r"""Adds a privilege tuple (of REST URI and its access level) to an existing role.
### Required parameters
* `owner.uuid` - UUID of the SVM that houses this role.
* `name` - Name of the role to be updated.
* `path` - REST URI path (example: <i>/api/storage/volumes</i>). Can be a resource-qualified endpoint (example: <i>/api/storage/volumes/43256a71-be02-474d-a2a9-9642e12a6a2c/snapshots</i>). Currently, resource-qualified endpoints are limited to the "snapshots" endpoint: <i>/api/storage/volumes/{volume.uuid}/snapshots</i> and <i>/api/storage/volumes/\*/snapshots</i>. "*" is a wildcard character denoting "all" volumes.
* `access` - Desired access level for the REST URI path (one of "all", "readonly" or "none").
### Related ONTAP commands
* `security login rest-role create`
### Learn more
* [`DOC /security/roles/{owner.uuid}/{name}/privileges`](#docs-security-security_roles_{owner.uuid}_{name}_privileges)
* [`DOC /security/roles`](#docs-security-security_roles)
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
        records: Iterable["RolePrivilege"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a privilege tuple (of REST URI and its access level) from the role. The REST URI can be a resource-qualified endpoint. Currently, the only supported resource-qualified endpoints are <i>/api/storage/volumes/{volume.uuid}/snapshots</i> and <i>/api/storage/volumes/\*/snapshots</i>. "*" is a wildcard character denoting "all" volumes.
### Required parameters
* `owner.uuid` - UUID of the SVM which houses this role.
* `name` - Name of the role to be updated.
* `path` - Constituent REST API path to be deleted from this role. Can be a resource-qualified endpoint (example: <i>/api/storage/volumes/43256a71-be02-474d-a2a9-9642e12a6a2c/snapshots</i>). Currently, resource-qualified endpoints are limited to the "snapshots" endpoint: <i>/api/storage/volumes/{volume.uuid}/snapshots</i> and <i>/api/storage/volumes/\*/snapshots</i>. "*" is a wildcard character denoting "all" volumes.
### Related ONTAP commands
* `security login rest-role delete`
### Learn more
* [`DOC /security/roles/{owner.uuid}/{name}/privileges/{path}`](#docs-security-security_roles_{owner.uuid}_{name}_privileges_{path})
* [`DOC /security/roles`](#docs-security-security_roles)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves privilege details of the specified role.
### Related ONTAP commands
* `security login rest-role show`
### Learn more
* [`DOC /security/roles/{owner.uuid}/{name}/privileges`](#docs-security-security_roles_{owner.uuid}_{name}_privileges)
* [`DOC /security/roles`](#docs-security-security_roles)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the privilege level for a REST API path for the specified role. The REST API path can be a resource-qualified endpoint. Currently, the only supported resource-qualified endpoints are <i>/api/storage/volumes/{volume.uuid}/snapshots</i> and <i>/api/storage/volumes/\*/snapshots</i>. "*" is a wildcard character denoting "all" volumes.
### Related ONTAP commands
* `security login rest-role show`
### Learn more
* [`DOC /security/roles/{owner.uuid}/{name}/privileges/{path}`](#docs-security-security_roles_{owner.uuid}_{name}_privileges_{path})
* [`DOC /security/roles`](#docs-security-security_roles)
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
        r"""Adds a privilege tuple (of REST URI and its access level) to an existing role.
### Required parameters
* `owner.uuid` - UUID of the SVM that houses this role.
* `name` - Name of the role to be updated.
* `path` - REST URI path (example: <i>/api/storage/volumes</i>). Can be a resource-qualified endpoint (example: <i>/api/storage/volumes/43256a71-be02-474d-a2a9-9642e12a6a2c/snapshots</i>). Currently, resource-qualified endpoints are limited to the "snapshots" endpoint: <i>/api/storage/volumes/{volume.uuid}/snapshots</i> and <i>/api/storage/volumes/\*/snapshots</i>. "*" is a wildcard character denoting "all" volumes.
* `access` - Desired access level for the REST URI path (one of "all", "readonly" or "none").
### Related ONTAP commands
* `security login rest-role create`
### Learn more
* [`DOC /security/roles/{owner.uuid}/{name}/privileges`](#docs-security-security_roles_{owner.uuid}_{name}_privileges)
* [`DOC /security/roles`](#docs-security-security_roles)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="role privilege create")
        async def role_privilege_create(
            name,
            owner_uuid,
            links: dict = None,
            access: str = None,
            path: str = None,
        ) -> ResourceTable:
            """Create an instance of a RolePrivilege resource

            Args:
                links: 
                access: 
                path: REST URI/endpoint
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if access is not None:
                kwargs["access"] = access
            if path is not None:
                kwargs["path"] = path

            resource = RolePrivilege(
                name,
                owner_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create RolePrivilege: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the privilege level for a REST API path. The REST API path can be a resource-qualified endpoint. Currently, the only supported resource-qualified endpoints are <i>/api/storage/volumes/{volume.uuid}/snapshots</i> and <i>/api/storage/volumes/\*/snapshots</i>. "*" is a wildcard character denoting "all" volumes.
### Required parameters
* `owner.uuid` - UUID of the SVM that houses this role.
* `name` - Name of the role to be updated.
* `path` - Constituent REST API path whose access level is to be updated. Can be a resource-qualified endpoint (example: <i>/api/storage/volumes/43256a71-be02-474d-a2a9-9642e12a6a2c/snapshots</i>). Currently, resource-qualified endpoints are limited to the "snapshots" endpoint: <i>/api/storage/volumes/{volume.uuid}/snapshots</i> and <i>/api/storage/volumes/\*/snapshots</i>. "*" is a wildcard character denoting "all" volumes.
* `access` - Access level for the path (one of "all", "readonly", or "none")
### Related ONTAP commands
* `security login rest-role modify`
### Learn more
* [`DOC /security/roles/{owner.uuid}/{name}/privileges/{path}`](#docs-security-security_roles_{owner.uuid}_{name}_privileges_{path})
* [`DOC /security/roles`](#docs-security-security_roles)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="role privilege modify")
        async def role_privilege_modify(
            name,
            owner_uuid,
            access: str = None,
            query_access: str = None,
            path: str = None,
            query_path: str = None,
        ) -> ResourceTable:
            """Modify an instance of a RolePrivilege resource

            Args:
                access: 
                query_access: 
                path: REST URI/endpoint
                query_path: REST URI/endpoint
            """

            kwargs = {}
            changes = {}
            if query_access is not None:
                kwargs["access"] = query_access
            if query_path is not None:
                kwargs["path"] = query_path

            if access is not None:
                changes["access"] = access
            if path is not None:
                changes["path"] = path

            if hasattr(RolePrivilege, "find"):
                resource = RolePrivilege.find(
                    name,
                    owner_uuid,
                    **kwargs
                )
            else:
                resource = RolePrivilege(name,owner_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify RolePrivilege: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a privilege tuple (of REST URI and its access level) from the role. The REST URI can be a resource-qualified endpoint. Currently, the only supported resource-qualified endpoints are <i>/api/storage/volumes/{volume.uuid}/snapshots</i> and <i>/api/storage/volumes/\*/snapshots</i>. "*" is a wildcard character denoting "all" volumes.
### Required parameters
* `owner.uuid` - UUID of the SVM which houses this role.
* `name` - Name of the role to be updated.
* `path` - Constituent REST API path to be deleted from this role. Can be a resource-qualified endpoint (example: <i>/api/storage/volumes/43256a71-be02-474d-a2a9-9642e12a6a2c/snapshots</i>). Currently, resource-qualified endpoints are limited to the "snapshots" endpoint: <i>/api/storage/volumes/{volume.uuid}/snapshots</i> and <i>/api/storage/volumes/\*/snapshots</i>. "*" is a wildcard character denoting "all" volumes.
### Related ONTAP commands
* `security login rest-role delete`
### Learn more
* [`DOC /security/roles/{owner.uuid}/{name}/privileges/{path}`](#docs-security-security_roles_{owner.uuid}_{name}_privileges_{path})
* [`DOC /security/roles`](#docs-security-security_roles)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="role privilege delete")
        async def role_privilege_delete(
            name,
            owner_uuid,
            access: str = None,
            path: str = None,
        ) -> None:
            """Delete an instance of a RolePrivilege resource

            Args:
                access: 
                path: REST URI/endpoint
            """

            kwargs = {}
            if access is not None:
                kwargs["access"] = access
            if path is not None:
                kwargs["path"] = path

            if hasattr(RolePrivilege, "find"):
                resource = RolePrivilege.find(
                    name,
                    owner_uuid,
                    **kwargs
                )
            else:
                resource = RolePrivilege(name,owner_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete RolePrivilege: %s" % err)


