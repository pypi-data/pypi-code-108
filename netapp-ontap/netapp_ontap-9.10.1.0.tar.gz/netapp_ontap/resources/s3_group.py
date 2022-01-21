r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
An S3 group consists of one or many users. Policies are attached to the S3 group to have access control over S3 resources at group level.
## Examples
### Retrieving all fields for all S3 groups of an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Group

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            S3Group.get_collection(
                "12f3ba4c-7ae0-11e9-8c06-0050568ea123", fields="*", return_timeout=15
            )
        )
    )

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    S3Group(
        {
            "svm": {"uuid": "02c9e252-41be-11e9-81d5-00a0986138f7", "name": "svm1"},
            "id": 5,
            "comment": "Admin group",
            "users": [{"name": "User1"}, {"name": "User2"}, {"name": "User3"}],
            "name": "Admin-Group",
            "policies": [{"name": "Policy1"}, {"name": "Policy2"}, {"name": "Policy3"}],
        }
    ),
    S3Group(
        {
            "svm": {"uuid": "02c9e252-41be-11e9-81d5-00a0986138f7", "name": "svm1"},
            "id": 6,
            "comment": "Admin group",
            "users": [{"name": "User1"}, {"name": "User2"}, {"name": "User6"}],
            "name": "Admin-Group1",
            "policies": [{"name": "Policy1"}, {"name": "Policy2"}, {"name": "Policy3"}],
        }
    ),
]

```
</div>
</div>

### Retrieving the specified group in the SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Group

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Group("12f3ba4c-7ae0-11e9-8c06-0050568ea123", id=5)
    resource.get(fields="*")
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
S3Group(
    {
        "svm": {"uuid": "02c9e252-41be-11e9-81d5-00a0986138f7", "name": "svm1"},
        "id": 5,
        "comment": "Admin group",
        "users": [{"name": "User1"}, {"name": "User2"}, {"name": "User3"}],
        "name": "Admin-Group",
        "policies": [{"name": "Policy1"}, {"name": "Policy2"}, {"name": "Policy3"}],
    }
)

```
</div>
</div>

### Creating an S3 group for an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Group

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Group("12f3ba4c-7ae0-11e9-8c06-0050568ea123")
    resource.comment = "Admin group"
    resource.name = "Admin-Group"
    resource.policies = [{"name": "Policy1"}, {"name": "Policy2"}, {"name": "Policy3"}]
    resource.users = [{"name": "User1"}, {"name": "User2"}, {"name": "User3"}]
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
S3Group(
    {
        "svm": {"uuid": "02c9e252-41be-11e9-81d5-00a0986138f7", "name": "svm1"},
        "id": 5,
        "comment": "Admin group",
        "users": [{"name": "User1"}, {"name": "User2"}, {"name": "User3"}],
        "name": "Admin-Group",
        "policies": [{"name": "Policy1"}, {"name": "Policy2"}, {"name": "Policy3"}],
    }
)

```
</div>
</div>

### Updating an S3 group for an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Group

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Group("12f3ba4c-7ae0-11e9-8c06-0050568ea123", id=5)
    resource.comment = "Admin group"
    resource.name = "Admin-Group"
    resource.policies = [{"name": "Policy1"}]
    resource.users = [{"name": "user-1"}]
    resource.patch()

```

### Deleting an S3 group for a specified SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Group

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Group("12f3ba4c-7ae0-11e9-8c06-0050568ea123", id=5)
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


__all__ = ["S3Group", "S3GroupSchema"]
__pdoc__ = {
    "S3GroupSchema.resource": False,
    "S3Group.s3_group_show": False,
    "S3Group.s3_group_create": False,
    "S3Group.s3_group_modify": False,
    "S3Group.s3_group_delete": False,
}


class S3GroupSchema(ResourceSchema):
    """The fields of the S3Group object"""

    comment = fields.Str(
        data_key="comment",
        validate=len_validation(minimum=0, maximum=256),
    )
    r""" Can contain any additional information about the group being created or modified.

Example: Admin group """

    id = Size(
        data_key="id",
    )
    r""" Specifies a unique group ID used to identify a particular group. This parameter should not be specified in the POST method. A group ID is automatically generated and it is retrieved using the GET method. Group id is SVM scoped.

Example: 5 """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=1, maximum=128),
    )
    r""" Specifies the name of the group. A group name length can range from 1 to 128 characters and can only contain the following combination of characters 0-9, A-Z, a-z, "_", "+", "=", ",", ".","@", and "-".

Example: Admin-Group """

    policies = fields.List(fields.Nested("netapp_ontap.resources.s3_policy.S3PolicySchema", unknown=EXCLUDE), data_key="policies")
    r""" Specifies a list of policies that are attached to the group. The wildcard character "*" is a valid value for specifying all policies. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the s3_group. """

    users = fields.List(fields.Nested("netapp_ontap.resources.s3_user.S3UserSchema", unknown=EXCLUDE), data_key="users")
    r""" Specifies the list of users who belong to the group. """

    @property
    def resource(self):
        return S3Group

    gettable_fields = [
        "comment",
        "id",
        "name",
        "policies.links",
        "policies.name",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "users.links",
        "users.name",
    ]
    """comment,id,name,policies.links,policies.name,svm.links,svm.name,svm.uuid,users.links,users.name,"""

    patchable_fields = [
        "comment",
        "name",
        "policies.name",
        "svm.name",
        "svm.uuid",
        "users.name",
    ]
    """comment,name,policies.name,svm.name,svm.uuid,users.name,"""

    postable_fields = [
        "comment",
        "name",
        "policies.name",
        "svm.name",
        "svm.uuid",
        "users.name",
    ]
    """comment,name,policies.name,svm.name,svm.uuid,users.name,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in S3Group.get_collection(fields=field)]
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
            raise NetAppRestError("S3Group modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class S3Group(Resource):
    r""" This is a container for S3 user groups. """

    _schema = S3GroupSchema
    _path = "/api/protocols/s3/services/{svm[uuid]}/groups"
    _keys = ["svm.uuid", "id"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the S3 group's SVM configuration.
### Related ONTAP commands
* `vserver object-store-server group show`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/groups`](#docs-object-store-protocols_s3_services_{svm.uuid}_groups)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 group show")
        def s3_group_show(
            svm_uuid,
            comment: Choices.define(_get_field_list("comment"), cache_choices=True, inexact=True)=None,
            id: Choices.define(_get_field_list("id"), cache_choices=True, inexact=True)=None,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["comment", "id", "name", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of S3Group resources

            Args:
                comment: Can contain any additional information about the group being created or modified.
                id: Specifies a unique group ID used to identify a particular group. This parameter should not be specified in the POST method. A group ID is automatically generated and it is retrieved using the GET method. Group id is SVM scoped.
                name: Specifies the name of the group. A group name length can range from 1 to 128 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return S3Group.get_collection(
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
        """Returns a count of all S3Group resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["S3Group"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the S3 group configuration of an SVM.
### Important notes
- The following fields can be modified for a group:
* `name` - Group name that needs to be modified.
* `users` - List of users present in the group.
* `policies` - List of policies to be attached to this group.
### Recommended optional properties
* `comment` - Short description about the S3 Group.
### Related ONTAP commands
* `vserver object-store-server group modify`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/groups`](#docs-object-store-protocols_s3_services_{svm.uuid}_groups)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["S3Group"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["S3Group"], NetAppResponse]:
        r"""Creates the S3 group configuration.
### Important notes
- Each SVM can have one or more s3 group configurations.
### Required properties
* `svm.uuid` - Existing SVM in which to create the user configuration.
* `name` - Group name that is to be created.
* `users` - List of users to be added into the group.
* `policies` - List of policies are to be attached to this group.
### Recommended optional properties
* `comment` - Short description about the S3 Group.
### Related ONTAP commands
* `vserver object-store-server group create`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/groups`](#docs-object-store-protocols_s3_services_{svm.uuid}_groups)
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
        records: Iterable["S3Group"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the S3 group configuration of an SVM.
### Related ONTAP commands
* `vserver object-store-server group delete`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/groups`](#docs-object-store-protocols_s3_services_{svm.uuid}_groups)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the S3 group's SVM configuration.
### Related ONTAP commands
* `vserver object-store-server group show`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/groups`](#docs-object-store-protocols_s3_services_{svm.uuid}_groups)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the S3 group configuration of an SVM.
### Related ONTAP commands
* `vserver object-store-server group show`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/groups`](#docs-object-store-protocols_s3_services_{svm.uuid}_groups)
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
        r"""Creates the S3 group configuration.
### Important notes
- Each SVM can have one or more s3 group configurations.
### Required properties
* `svm.uuid` - Existing SVM in which to create the user configuration.
* `name` - Group name that is to be created.
* `users` - List of users to be added into the group.
* `policies` - List of policies are to be attached to this group.
### Recommended optional properties
* `comment` - Short description about the S3 Group.
### Related ONTAP commands
* `vserver object-store-server group create`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/groups`](#docs-object-store-protocols_s3_services_{svm.uuid}_groups)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 group create")
        async def s3_group_create(
            svm_uuid,
            comment: str = None,
            id: Size = None,
            name: str = None,
            policies: dict = None,
            svm: dict = None,
            users: dict = None,
        ) -> ResourceTable:
            """Create an instance of a S3Group resource

            Args:
                comment: Can contain any additional information about the group being created or modified.
                id: Specifies a unique group ID used to identify a particular group. This parameter should not be specified in the POST method. A group ID is automatically generated and it is retrieved using the GET method. Group id is SVM scoped.
                name: Specifies the name of the group. A group name length can range from 1 to 128 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
                policies: Specifies a list of policies that are attached to the group. The wildcard character \"*\" is a valid value for specifying all policies.
                svm: 
                users: Specifies the list of users who belong to the group.
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if policies is not None:
                kwargs["policies"] = policies
            if svm is not None:
                kwargs["svm"] = svm
            if users is not None:
                kwargs["users"] = users

            resource = S3Group(
                svm_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create S3Group: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the S3 group configuration of an SVM.
### Important notes
- The following fields can be modified for a group:
* `name` - Group name that needs to be modified.
* `users` - List of users present in the group.
* `policies` - List of policies to be attached to this group.
### Recommended optional properties
* `comment` - Short description about the S3 Group.
### Related ONTAP commands
* `vserver object-store-server group modify`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/groups`](#docs-object-store-protocols_s3_services_{svm.uuid}_groups)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 group modify")
        async def s3_group_modify(
            svm_uuid,
            comment: str = None,
            query_comment: str = None,
            id: Size = None,
            query_id: Size = None,
            name: str = None,
            query_name: str = None,
        ) -> ResourceTable:
            """Modify an instance of a S3Group resource

            Args:
                comment: Can contain any additional information about the group being created or modified.
                query_comment: Can contain any additional information about the group being created or modified.
                id: Specifies a unique group ID used to identify a particular group. This parameter should not be specified in the POST method. A group ID is automatically generated and it is retrieved using the GET method. Group id is SVM scoped.
                query_id: Specifies a unique group ID used to identify a particular group. This parameter should not be specified in the POST method. A group ID is automatically generated and it is retrieved using the GET method. Group id is SVM scoped.
                name: Specifies the name of the group. A group name length can range from 1 to 128 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
                query_name: Specifies the name of the group. A group name length can range from 1 to 128 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
            """

            kwargs = {}
            changes = {}
            if query_comment is not None:
                kwargs["comment"] = query_comment
            if query_id is not None:
                kwargs["id"] = query_id
            if query_name is not None:
                kwargs["name"] = query_name

            if comment is not None:
                changes["comment"] = comment
            if id is not None:
                changes["id"] = id
            if name is not None:
                changes["name"] = name

            if hasattr(S3Group, "find"):
                resource = S3Group.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = S3Group(svm_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify S3Group: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the S3 group configuration of an SVM.
### Related ONTAP commands
* `vserver object-store-server group delete`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/groups`](#docs-object-store-protocols_s3_services_{svm.uuid}_groups)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 group delete")
        async def s3_group_delete(
            svm_uuid,
            comment: str = None,
            id: Size = None,
            name: str = None,
        ) -> None:
            """Delete an instance of a S3Group resource

            Args:
                comment: Can contain any additional information about the group being created or modified.
                id: Specifies a unique group ID used to identify a particular group. This parameter should not be specified in the POST method. A group ID is automatically generated and it is retrieved using the GET method. Group id is SVM scoped.
                name: Specifies the name of the group. A group name length can range from 1 to 128 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name

            if hasattr(S3Group, "find"):
                resource = S3Group.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = S3Group(svm_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete S3Group: %s" % err)


