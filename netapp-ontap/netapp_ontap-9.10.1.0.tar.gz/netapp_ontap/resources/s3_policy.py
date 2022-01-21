r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
An S3 policy is an object that when associated with a resource, defines their permissions. Buckets and objects are defined as resources. Policies are used to manage access to these resources.
## Examples
### Retrieving all fields for all S3 policies of an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Policy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            S3Policy.get_collection(
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
    S3Policy(
        {
            "svm": {"uuid": "02c9e252-41be-11e9-81d5-00a0986138f7", "name": "svm1"},
            "statements": [
                {
                    "effect": "allow",
                    "resources": ["bucket1", "bucket1/*"],
                    "actions": ["*"],
                    "sid": "FullAccessToBucket1",
                    "index": 0,
                },
                {
                    "effect": "deny",
                    "resources": ["*"],
                    "actions": ["DeleteObject"],
                    "sid": "DenyDeleteObjectAccessToAllResources",
                    "index": 1,
                },
            ],
            "comment": "S3 policy.",
            "name": "Policy1",
        }
    ),
    S3Policy(
        {
            "svm": {"uuid": "02c9e252-41be-11e9-81d5-00a0986138f7", "name": "svm1"},
            "statements": [
                {
                    "effect": "allow",
                    "resources": ["*"],
                    "actions": ["GetObject"],
                    "sid": "AllowGetObjectAccessToAllResources",
                    "index": 3,
                },
                {
                    "effect": "deny",
                    "resources": ["*"],
                    "actions": ["*"],
                    "sid": "DenyAccessToAllResources",
                    "index": 3,
                },
            ],
            "comment": "S3 policy 2.",
            "name": "Policy2",
        }
    ),
]

```
</div>
</div>

### Retrieving the specified policy in the SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Policy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Policy("12f3ba4c-7ae0-11e9-8c06-0050568ea123", name="Policy1")
    resource.get(fields="*")
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
S3Policy(
    {
        "svm": {"uuid": "02c9e252-41be-11e9-81d5-00a0986138f7", "name": "svm1"},
        "statements": [
            {
                "effect": "deny",
                "resources": ["*"],
                "actions": [
                    "GetObject",
                    "PutObject",
                    "DeleteObject",
                    "ListBucket",
                    "ListMyBuckets",
                    "ListBucketMultipartUploads",
                    "ListMultipartUploadParts",
                    "GetObjectTagging",
                    "PutObjectTagging",
                    "DeleteObjectTagging",
                ],
                "sid": "DenyAccessToAllResources",
                "index": 0,
            }
        ],
        "comment": "S3 policy.",
        "name": "Policy1",
    }
)

```
</div>
</div>

### Creating an S3 policy for an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Policy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Policy("12f3ba4c-7ae0-11e9-8c06-0050568ea123")
    resource.comment = "S3 policy."
    resource.name = "Policy1"
    resource.statements = [
        {
            "actions": ["ListBucket", "ListMyBuckets"],
            "effect": "allow",
            "resources": ["*"],
            "sid": "AllowListAccessToAllResources",
        }
    ]
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
S3Policy(
    {
        "svm": {"uuid": "02c9e252-41be-11e9-81d5-00a0986138f7", "name": "svm1"},
        "statements": [
            {
                "effect": "allow",
                "resources": ["*"],
                "actions": ["ListBucket", "ListMyBuckets"],
                "sid": "AllowListAccessToAllResources",
                "index": 5,
            }
        ],
        "comment": "S3 policy.",
        "name": "Policy1",
    }
)

```
</div>
</div>

### Updating an S3 policy for an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Policy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Policy("12f3ba4c-7ae0-11e9-8c06-0050568ea123", name="Policy1")
    resource.comment = "S3 policy."
    resource.statements = [
        {
            "actions": [
                "GetObject",
                "PutObject",
                "DeleteObject",
                "ListBucket",
                "ListMyBuckets",
            ],
            "effect": "allow",
            "resources": ["bucket1", "bucket1/*"],
            "sid": "FullAccessToAllResources",
        }
    ]
    resource.patch()

```

### Deleting an S3 policy for a specified SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Policy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Policy("12f3ba4c-7ae0-11e9-8c06-0050568ea123", name="Policy1")
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


__all__ = ["S3Policy", "S3PolicySchema"]
__pdoc__ = {
    "S3PolicySchema.resource": False,
    "S3Policy.s3_policy_show": False,
    "S3Policy.s3_policy_create": False,
    "S3Policy.s3_policy_modify": False,
    "S3Policy.s3_policy_delete": False,
}


class S3PolicySchema(ResourceSchema):
    """The fields of the S3Policy object"""

    comment = fields.Str(
        data_key="comment",
        validate=len_validation(minimum=0, maximum=256),
    )
    r""" Can contain any additional information about the S3 policy.

Example: S3 policy. """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=1, maximum=128),
    )
    r""" Specifies the name of the policy. A policy name length can range from 1 to 128 characters and can only contain the following combination of characters 0-9, A-Z, a-z, "_", "+", "=", ",", ".","@", and "-".

Example: Policy1 """

    read_only = fields.Boolean(
        data_key="read-only",
    )
    r""" Specifies whether or not the s3 policy is read only. This parameter should not be specified in the POST method. """

    statements = fields.List(fields.Nested("netapp_ontap.models.s3_policy_statement.S3PolicyStatementSchema", unknown=EXCLUDE), data_key="statements")
    r""" Specifies the policy statements. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the s3_policy. """

    @property
    def resource(self):
        return S3Policy

    gettable_fields = [
        "comment",
        "name",
        "read_only",
        "statements",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """comment,name,read_only,statements,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "comment",
        "statements",
        "svm.name",
        "svm.uuid",
    ]
    """comment,statements,svm.name,svm.uuid,"""

    postable_fields = [
        "comment",
        "name",
        "statements",
        "svm.name",
        "svm.uuid",
    ]
    """comment,name,statements,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in S3Policy.get_collection(fields=field)]
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
            raise NetAppRestError("S3Policy modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class S3Policy(Resource):
    r""" An S3 policy is an object. It defines resource (bucket, folder or object) permissions. These policies get evaluated when an object store user user makes a request. Permissions in the policies determine whether the request is allowed or denied. """

    _schema = S3PolicySchema
    _path = "/api/protocols/s3/services/{svm[uuid]}/policies"
    _keys = ["svm.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the S3 policies SVM configuration.
### Related ONTAP commands
* `vserver object-store-server policy show`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/policies`](#docs-object-store-protocols_s3_services_{svm.uuid}_policies)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 policy show")
        def s3_policy_show(
            svm_uuid,
            comment: Choices.define(_get_field_list("comment"), cache_choices=True, inexact=True)=None,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            read_only: Choices.define(_get_field_list("read_only"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["comment", "name", "read_only", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of S3Policy resources

            Args:
                comment: Can contain any additional information about the S3 policy.
                name: Specifies the name of the policy. A policy name length can range from 1 to 128 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
                read_only: Specifies whether or not the s3 policy is read only. This parameter should not be specified in the POST method.
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if name is not None:
                kwargs["name"] = name
            if read_only is not None:
                kwargs["read_only"] = read_only
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return S3Policy.get_collection(
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
        """Returns a count of all S3Policy resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["S3Policy"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the S3 policy configuration of an SVM.
### Important notes
- The following fields can be modified for a policy:
  * `comment` - Any information related to the policy.
  * `statements` - Specifies the array of policy statements.
### Related ONTAP commands
* `vserver object-store-server policy modify`
* `vserver object-store-server policy modify-statement`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/policies`](#docs-object-store-protocols_s3_services_{svm.uuid}_policies)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["S3Policy"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["S3Policy"], NetAppResponse]:
        r"""Creates the S3 policy configuration.
### Important notes
- Each SVM can have one or more s3 policy configurations.
### Required properties
* `svm.uuid` - Existing SVM in which to create the s3 policy configuration.
* `name` - Policy name that is to be created.
### Recommended optional properties
* `comment` - Short description about the S3 policy.
* `statements.effect` - Indicates whether to allow or deny access.
* `statements.actions` - List of actions that can be allowed or denied access. Example: GetObject, PutObject, DeleteObject, ListBucket, ListMyBuckets, ListBucketMultipartUploads, ListMultipartUploadParts, GetObjectTagging, PutObjectTagging, DeleteObjectTagging.
* `statements.resources` - Buckets or objects that can be allowed or denied access.
* `statements.sid` - Statement identifier providing additional information about the statement.
### Related ONTAP commands
* `vserver object-store-server policy create`
* `vserver object-store-server policy add-statement`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/policies`](#docs-object-store-protocols_s3_services_{svm.uuid}_policies)
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
        records: Iterable["S3Policy"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the S3 policy configuration of an SVM.
### Related ONTAP commands
* `vserver object-store-server policy delete`
* `vserver object-store-server policy delete-statement`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/policies`](#docs-object-store-protocols_s3_services_{svm.uuid}_policies)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the S3 policies SVM configuration.
### Related ONTAP commands
* `vserver object-store-server policy show`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/policies`](#docs-object-store-protocols_s3_services_{svm.uuid}_policies)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the S3 policy configuration of an SVM.
### Related ONTAP commands
* `vserver object-store-server policy show`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/policies`](#docs-object-store-protocols_s3_services_{svm.uuid}_policies)
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
        r"""Creates the S3 policy configuration.
### Important notes
- Each SVM can have one or more s3 policy configurations.
### Required properties
* `svm.uuid` - Existing SVM in which to create the s3 policy configuration.
* `name` - Policy name that is to be created.
### Recommended optional properties
* `comment` - Short description about the S3 policy.
* `statements.effect` - Indicates whether to allow or deny access.
* `statements.actions` - List of actions that can be allowed or denied access. Example: GetObject, PutObject, DeleteObject, ListBucket, ListMyBuckets, ListBucketMultipartUploads, ListMultipartUploadParts, GetObjectTagging, PutObjectTagging, DeleteObjectTagging.
* `statements.resources` - Buckets or objects that can be allowed or denied access.
* `statements.sid` - Statement identifier providing additional information about the statement.
### Related ONTAP commands
* `vserver object-store-server policy create`
* `vserver object-store-server policy add-statement`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/policies`](#docs-object-store-protocols_s3_services_{svm.uuid}_policies)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 policy create")
        async def s3_policy_create(
            svm_uuid,
            comment: str = None,
            name: str = None,
            read_only: bool = None,
            statements: dict = None,
            svm: dict = None,
        ) -> ResourceTable:
            """Create an instance of a S3Policy resource

            Args:
                comment: Can contain any additional information about the S3 policy.
                name: Specifies the name of the policy. A policy name length can range from 1 to 128 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
                read_only: Specifies whether or not the s3 policy is read only. This parameter should not be specified in the POST method.
                statements: Specifies the policy statements.
                svm: 
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if name is not None:
                kwargs["name"] = name
            if read_only is not None:
                kwargs["read_only"] = read_only
            if statements is not None:
                kwargs["statements"] = statements
            if svm is not None:
                kwargs["svm"] = svm

            resource = S3Policy(
                svm_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create S3Policy: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the S3 policy configuration of an SVM.
### Important notes
- The following fields can be modified for a policy:
  * `comment` - Any information related to the policy.
  * `statements` - Specifies the array of policy statements.
### Related ONTAP commands
* `vserver object-store-server policy modify`
* `vserver object-store-server policy modify-statement`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/policies`](#docs-object-store-protocols_s3_services_{svm.uuid}_policies)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 policy modify")
        async def s3_policy_modify(
            svm_uuid,
            comment: str = None,
            query_comment: str = None,
            name: str = None,
            query_name: str = None,
            read_only: bool = None,
            query_read_only: bool = None,
        ) -> ResourceTable:
            """Modify an instance of a S3Policy resource

            Args:
                comment: Can contain any additional information about the S3 policy.
                query_comment: Can contain any additional information about the S3 policy.
                name: Specifies the name of the policy. A policy name length can range from 1 to 128 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
                query_name: Specifies the name of the policy. A policy name length can range from 1 to 128 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
                read_only: Specifies whether or not the s3 policy is read only. This parameter should not be specified in the POST method.
                query_read_only: Specifies whether or not the s3 policy is read only. This parameter should not be specified in the POST method.
            """

            kwargs = {}
            changes = {}
            if query_comment is not None:
                kwargs["comment"] = query_comment
            if query_name is not None:
                kwargs["name"] = query_name
            if query_read_only is not None:
                kwargs["read_only"] = query_read_only

            if comment is not None:
                changes["comment"] = comment
            if name is not None:
                changes["name"] = name
            if read_only is not None:
                changes["read_only"] = read_only

            if hasattr(S3Policy, "find"):
                resource = S3Policy.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = S3Policy(svm_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify S3Policy: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the S3 policy configuration of an SVM.
### Related ONTAP commands
* `vserver object-store-server policy delete`
* `vserver object-store-server policy delete-statement`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/policies`](#docs-object-store-protocols_s3_services_{svm.uuid}_policies)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 policy delete")
        async def s3_policy_delete(
            svm_uuid,
            comment: str = None,
            name: str = None,
            read_only: bool = None,
        ) -> None:
            """Delete an instance of a S3Policy resource

            Args:
                comment: Can contain any additional information about the S3 policy.
                name: Specifies the name of the policy. A policy name length can range from 1 to 128 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
                read_only: Specifies whether or not the s3 policy is read only. This parameter should not be specified in the POST method.
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if name is not None:
                kwargs["name"] = name
            if read_only is not None:
                kwargs["read_only"] = read_only

            if hasattr(S3Policy, "find"):
                resource = S3Policy.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = S3Policy(svm_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete S3Policy: %s" % err)


