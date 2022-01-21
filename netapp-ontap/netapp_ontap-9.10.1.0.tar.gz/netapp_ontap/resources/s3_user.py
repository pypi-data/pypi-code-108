r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
An S3 user account is created on the S3 server. Buckets that are created for the server are associated with that user (as the owner of the buckets).
The creation of the user account involves generating a pair of keys "access" and "secret".
These keys are shared with clients (by the administrator out of band) who want to access the S3 server. The access_key is sent in the request and it identifies the user performing the operation. The client or server never send the secret_key over the wire.
Only the access_key can be retrieved from a GET operation. The secret_key along with the access_key is returned from a POST operation and from a PATCH operation if the administrator needs to regenerate the keys.
## Examples
### Retrieving S3 user configurations for a particular SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3User

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(S3User.get_collection("db2ec036-8375-11e9-99e1-0050568e3ed9", fields="*"))
    )

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    S3User(
        {
            "comment": "S3 user",
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/db2ec036-8375-11e9-99e1-0050568e3ed9"
                    }
                },
                "uuid": "db2ec036-8375-11e9-99e1-0050568e3ed9",
                "name": "vs1",
            },
            "name": "user-1",
            "access_key": "8OPlYd5gm53sTNkTNgrsJ0_4iHvw_Ir_9xtDhzGa3m2_a_Yhtv6Bm3Dq_Xv79Stq90BWa5NrTL7UQ2u_0xN0IW_x39cm1h3sn69fN6cf6STA48W05PAxuGED3NcR7rsn",
        }
    ),
    S3User(
        {
            "comment": "s3-user",
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/db2ec036-8375-11e9-99e1-0050568e3ed9"
                    }
                },
                "uuid": "db2ec036-8375-11e9-99e1-0050568e3ed9",
                "name": "vs1",
            },
            "name": "user-2",
            "access_key": "uYo34d4eR8a3is7JDSCY1xrNwL7gFMA338ZEX2mNrgJ34Kb4u98QNhBGT3ghs9GA2bzNdYBSn5_rBfjIY4mt36CMFE4d3g0L3Pa_2nXD6g6CAq_D0422LK__pbH6wvy8",
        }
    ),
]

```
</div>
</div>

### Retrieving the user configuration of a specific S3 user
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3User

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3User("db2ec036-8375-11e9-99e1-0050568e3ed9", name="user-1")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
S3User(
    {
        "comment": "s3-user",
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/db2ec036-8375-11e9-99e1-0050568e3ed9"}
            },
            "uuid": "db2ec036-8375-11e9-99e1-0050568e3ed9",
            "name": "vs1",
        },
        "name": "user-1",
        "access_key": "uYo34d4eR8a3is7JDSCY1xrNwL7gFMA338ZEX2mNrgJ34Kb4u98QNhBGT3ghs9GA2bzNdYBSn5_rBfjIY4mt36CMFE4d3g0L3Pa_2nXD6g6CAq_D0422LK__pbH6wvy8",
    }
)

```
</div>
</div>

### Creating an S3 user configuration
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3User

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3User("db2ec036-8375-11e9-99e1-0050568e3ed9")
    resource.name = "user-1"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
S3User(
    {
        "name": "user-1",
        "access_key": "8OPlYd5gm53sTNkTNgrsJ0_4iHvw_Ir_9xtDhzGa3m2_a_Yhtv6Bm3Dq_Xv79Stq90BWa5NrTL7UQ2u_0xN0IW_x39cm1h3sn69fN6cf6STA48W05PAxuGED3NcR7rsn",
    }
)

```
</div>
</div>

### Regenerating keys for a specific S3 user for the specified SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3User

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3User("db2ec036-8375-11e9-99e1-0050568e3ed9", name="user-2")
    resource.patch(hydrate=True, regenerate_keys=True)

```

### Deleting the specified S3 user configuration for a specified SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3User

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3User("03ce5c36-f269-11e8-8852-0050568e5298", name="user-2")
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


__all__ = ["S3User", "S3UserSchema"]
__pdoc__ = {
    "S3UserSchema.resource": False,
    "S3User.s3_user_show": False,
    "S3User.s3_user_create": False,
    "S3User.s3_user_modify": False,
    "S3User.s3_user_delete": False,
}


class S3UserSchema(ResourceSchema):
    """The fields of the S3User object"""

    access_key = fields.Str(
        data_key="access_key",
    )
    r""" Specifies the access key for the user.

Example: Pz3SB54G2B_6dsXQPrA5HrTPcf478qoAW6_Xx6qyqZ948AgZ_7YfCf_9nO87YoZmskxx3cq41U2JAH2M3_fs321B4rkzS3a_oC5_8u7D8j_45N8OsBCBPWGD_1d_ccfq """

    comment = fields.Str(
        data_key="comment",
        validate=len_validation(minimum=0, maximum=256),
    )
    r""" Can contain any additional information about the user being created or modified.

Example: S3 user """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=1, maximum=64),
    )
    r""" Specifies the name of the user. A user name length can range from 1 to 64 characters and can only contain the following combination of characters 0-9, A-Z, a-z, "_", "+", "=", ",", ".","@", and "-".

Example: user-1 """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the s3_user. """

    @property
    def resource(self):
        return S3User

    gettable_fields = [
        "access_key",
        "comment",
        "name",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """access_key,comment,name,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "comment",
        "svm.name",
        "svm.uuid",
    ]
    """comment,svm.name,svm.uuid,"""

    postable_fields = [
        "comment",
        "name",
        "svm.name",
        "svm.uuid",
    ]
    """comment,name,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in S3User.get_collection(fields=field)]
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
            raise NetAppRestError("S3User modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class S3User(Resource):
    r""" This is a container of S3 users. """

    _schema = S3UserSchema
    _path = "/api/protocols/s3/services/{svm[uuid]}/users"
    _keys = ["svm.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the S3 user's SVM configuration.
### Related ONTAP commands
* `vserver object-store-server user show`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/users`](#docs-object-store-protocols_s3_services_{svm.uuid}_users)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 user show")
        def s3_user_show(
            svm_uuid,
            access_key: Choices.define(_get_field_list("access_key"), cache_choices=True, inexact=True)=None,
            comment: Choices.define(_get_field_list("comment"), cache_choices=True, inexact=True)=None,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["access_key", "comment", "name", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of S3User resources

            Args:
                access_key: Specifies the access key for the user.
                comment: Can contain any additional information about the user being created or modified.
                name: Specifies the name of the user. A user name length can range from 1 to 64 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
            """

            kwargs = {}
            if access_key is not None:
                kwargs["access_key"] = access_key
            if comment is not None:
                kwargs["comment"] = comment
            if name is not None:
                kwargs["name"] = name
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return S3User.get_collection(
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
        """Returns a count of all S3User resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["S3User"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the S3 user configuration of an SVM.
### Important notes
- User access_key and secret_key pair can be regenerated using the PATCH operation.
- User access_key and secret_key is returned in a PATCH operation if the "regenerate_keys" field is specified as true.
### Recommended optional properties
* `regenerate_keys` - Specifies if secret_key and access_key need to be regenerated.
* `comment` - Any information related to the S3 user.
### Related ONTAP commands
* `vserver object-store-server user show`
* `vserver object-store-server user regenerate-keys`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/users`](#docs-object-store-protocols_s3_services_{svm.uuid}_users)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["S3User"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["S3User"], NetAppResponse]:
        r"""Creates the S3 user configuration.
### Important notes
- Each SVM can have one or more user configurations.
- If user creation is successful, a user access_key and secret_key is returned as part of the response.
### Required properties
* `svm.uuid` - Existing SVM in which to create the user configuration.
* `name` - User name that is to be created.
### Default property values
* `comment` - ""
### Related ONTAP commands
* `vserver object-store-server user create`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/users`](#docs-object-store-protocols_s3_services_{svm.uuid}_users)
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
        records: Iterable["S3User"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the S3 user configuration of an SVM.
### Related ONTAP commands
* `vserver object-store-server user delete`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/users`](#docs-object-store-protocols_s3_services_{svm.uuid}_users)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the S3 user's SVM configuration.
### Related ONTAP commands
* `vserver object-store-server user show`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/users`](#docs-object-store-protocols_s3_services_{svm.uuid}_users)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the S3 user configuration of an SVM.
### Related ONTAP commands
* `vserver object-store-server user show`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/users`](#docs-object-store-protocols_s3_services_{svm.uuid}_users)
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
        r"""Creates the S3 user configuration.
### Important notes
- Each SVM can have one or more user configurations.
- If user creation is successful, a user access_key and secret_key is returned as part of the response.
### Required properties
* `svm.uuid` - Existing SVM in which to create the user configuration.
* `name` - User name that is to be created.
### Default property values
* `comment` - ""
### Related ONTAP commands
* `vserver object-store-server user create`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/users`](#docs-object-store-protocols_s3_services_{svm.uuid}_users)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 user create")
        async def s3_user_create(
            svm_uuid,
            access_key: str = None,
            comment: str = None,
            name: str = None,
            svm: dict = None,
        ) -> ResourceTable:
            """Create an instance of a S3User resource

            Args:
                access_key: Specifies the access key for the user.
                comment: Can contain any additional information about the user being created or modified.
                name: Specifies the name of the user. A user name length can range from 1 to 64 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
                svm: 
            """

            kwargs = {}
            if access_key is not None:
                kwargs["access_key"] = access_key
            if comment is not None:
                kwargs["comment"] = comment
            if name is not None:
                kwargs["name"] = name
            if svm is not None:
                kwargs["svm"] = svm

            resource = S3User(
                svm_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create S3User: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the S3 user configuration of an SVM.
### Important notes
- User access_key and secret_key pair can be regenerated using the PATCH operation.
- User access_key and secret_key is returned in a PATCH operation if the "regenerate_keys" field is specified as true.
### Recommended optional properties
* `regenerate_keys` - Specifies if secret_key and access_key need to be regenerated.
* `comment` - Any information related to the S3 user.
### Related ONTAP commands
* `vserver object-store-server user show`
* `vserver object-store-server user regenerate-keys`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/users`](#docs-object-store-protocols_s3_services_{svm.uuid}_users)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 user modify")
        async def s3_user_modify(
            svm_uuid,
            access_key: str = None,
            query_access_key: str = None,
            comment: str = None,
            query_comment: str = None,
            name: str = None,
            query_name: str = None,
        ) -> ResourceTable:
            """Modify an instance of a S3User resource

            Args:
                access_key: Specifies the access key for the user.
                query_access_key: Specifies the access key for the user.
                comment: Can contain any additional information about the user being created or modified.
                query_comment: Can contain any additional information about the user being created or modified.
                name: Specifies the name of the user. A user name length can range from 1 to 64 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
                query_name: Specifies the name of the user. A user name length can range from 1 to 64 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
            """

            kwargs = {}
            changes = {}
            if query_access_key is not None:
                kwargs["access_key"] = query_access_key
            if query_comment is not None:
                kwargs["comment"] = query_comment
            if query_name is not None:
                kwargs["name"] = query_name

            if access_key is not None:
                changes["access_key"] = access_key
            if comment is not None:
                changes["comment"] = comment
            if name is not None:
                changes["name"] = name

            if hasattr(S3User, "find"):
                resource = S3User.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = S3User(svm_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify S3User: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the S3 user configuration of an SVM.
### Related ONTAP commands
* `vserver object-store-server user delete`
### Learn more
* [`DOC /protocols/s3/services/{svm.uuid}/users`](#docs-object-store-protocols_s3_services_{svm.uuid}_users)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 user delete")
        async def s3_user_delete(
            svm_uuid,
            access_key: str = None,
            comment: str = None,
            name: str = None,
        ) -> None:
            """Delete an instance of a S3User resource

            Args:
                access_key: Specifies the access key for the user.
                comment: Can contain any additional information about the user being created or modified.
                name: Specifies the name of the user. A user name length can range from 1 to 64 characters and can only contain the following combination of characters 0-9, A-Z, a-z, \"_\", \"+\", \"=\", \",\", \".\",\"@\", and \"-\".
            """

            kwargs = {}
            if access_key is not None:
                kwargs["access_key"] = access_key
            if comment is not None:
                kwargs["comment"] = comment
            if name is not None:
                kwargs["name"] = name

            if hasattr(S3User, "find"):
                resource = S3User.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = S3User(svm_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete S3User: %s" % err)


