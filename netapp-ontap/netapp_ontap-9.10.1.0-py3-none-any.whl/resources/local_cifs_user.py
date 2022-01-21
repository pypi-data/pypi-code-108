r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
The CIFS server can use local users for CIFS authentication. The local users can also be used for authorization when determining both share and file/directory access rights to data residing on the storage virtual machine (SVM).
You can use this API to display local user information and to control local user configurations.
## Retrieving local user information
You can use the local user GET endpoint to retrieve all of the local user configurations for data SVMs.
## Examples
### Retrieving all of the fields for local user configurations for all SVMs
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(LocalCifsUser.get_collection(fields="**")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    LocalCifsUser(
        {
            "membership": [{"name": "BUILTIN\\Administrators", "sid": "S-1-5-32-544"}],
            "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
            "sid": "S-1-5-21-256008430-3394229847-3930036330-500",
            "full_name": "",
            "account_disabled": False,
            "name": "CIFS_SERVER1\\Administrator",
            "description": "Built-in administrator account",
        }
    ),
    LocalCifsUser(
        {
            "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
            "sid": "S-1-5-21-256008430-3394229847-3930036330-1001",
            "full_name": "local user1",
            "account_disabled": False,
            "name": "CIFS_SERVER1\\user1",
            "description": "This is CIFS local user",
        }
    ),
    LocalCifsUser(
        {
            "membership": [
                {
                    "name": "CIFS_SERVER1\\grp1",
                    "sid": "S-1-5-21-256008430-3394229847-3930036330-1001",
                },
                {
                    "name": "CIFS_SERVER1\\grp2",
                    "sid": "S-1-5-21-256008430-3394229847-3930036330-1002",
                },
            ],
            "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
            "sid": "S-1-5-21-256008430-3394229847-3930036330-1002",
            "full_name": "local user2",
            "account_disabled": False,
            "name": "CIFS_SERVER1\\user2",
            "description": "This is CIFS local user",
        }
    ),
    LocalCifsUser(
        {
            "membership": [{"name": "BUILTIN\\Administrators", "sid": "S-1-5-32-544"}],
            "svm": {"uuid": "3f479a01-2971-11eb-88e1-0050568eefd4", "name": "vs2"},
            "sid": "S-1-5-21-1625922807-3304708894-3529444428-500",
            "full_name": "",
            "account_disabled": False,
            "name": "CIFS_SERVER2\\Administrator",
            "description": "Built-in administrator account",
        }
    ),
    LocalCifsUser(
        {
            "svm": {"uuid": "3f479a01-2971-11eb-88e1-0050568eefd4", "name": "vs2"},
            "sid": "S-1-5-21-1625922807-3304708894-3529444428-1001",
            "full_name": "local user1",
            "account_disabled": False,
            "name": "CIFS_SERVER2\\user1",
            "description": "This is CIFS local user",
        }
    ),
]

```
</div>
</div>

---
### Retrieving the local user configuration of a specific SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            LocalCifsUser.get_collection(
                fields="**", **{"svm.uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
            )
        )
    )

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    LocalCifsUser(
        {
            "membership": [{"name": "BUILTIN\\Administrators", "sid": "S-1-5-32-544"}],
            "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
            "sid": "S-1-5-21-256008430-3394229847-3930036330-500",
            "full_name": "",
            "account_disabled": False,
            "name": "CIFS_SERVER1\\Administrator",
            "description": "Built-in administrator account",
        }
    ),
    LocalCifsUser(
        {
            "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
            "sid": "S-1-5-21-256008430-3394229847-3930036330-1001",
            "full_name": "local user1",
            "account_disabled": False,
            "name": "CIFS_SERVER1\\user1",
            "description": "This is CIFS local user",
        }
    ),
    LocalCifsUser(
        {
            "membership": [
                {
                    "name": "CIFS_SERVER1\\grp1",
                    "sid": "S-1-5-21-256008430-3394229847-3930036330-1001",
                },
                {
                    "name": "CIFS_SERVER1\\grp2",
                    "sid": "S-1-5-21-256008430-3394229847-3930036330-1002",
                },
            ],
            "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
            "sid": "S-1-5-21-256008430-3394229847-3930036330-1002",
            "full_name": "local user2",
            "account_disabled": False,
            "name": "CIFS_SERVER1\\user2",
            "description": "This is CIFS local user",
        }
    ),
]

```
</div>
</div>

---
### Retrieving a local user configuration of a specific SVM and user
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsUser(
        sid="S-1-5-21-1625922807-3304708894-3529444428-1001",
        **{"svm.uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
LocalCifsUser(
    {
        "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
        "sid": "S-1-5-21-256008430-3394229847-3930036330-1001",
        "full_name": "local user1",
        "account_disabled": False,
        "name": "CIFS_SERVER1\\user1",
        "description": "This is CIFS local user",
    }
)

```
</div>
</div>

---
## Creating a local user configuration
The local user POST endpoint creates a local user configuration for the specified SVM.
## Examples
### Creating a local user configuration with all fields specified
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsUser()
    resource.account_disabled = False
    resource.description = "This is local user."
    resource.full_name = "user name"
    resource.name = "SMB_SERVER01\user"
    resource.password = "netapp1N"
    resource.svm = {"name": "vs1", "uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
    resource.post(hydrate=True)
    print(resource)

```

---
### Creating a local user configuration with only mandatory fields specified
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsUser()
    resource.name = "user1"
    resource.password = "netapp1N"
    resource.svm = {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
    resource.post(hydrate=True)
    print(resource)

```

---
## Updating a local user configuration
The local user PATCH endpoint updates the local user configuration for the specified user and SVM.
### Updating a local user name and password
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsUser(
        sid="S-1-5-21-1625922807-3304708894-3529444428-1001",
        **{"svm.uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
    )
    resource.name = "new_user1"
    resource.password = "netapp1Net"
    resource.patch()

```

---
## Deleting a local user configuration
The local user DELETE endpoint deletes the specified local user for the specified SVM. The following example shows a DELETE operation:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsUser

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsUser(
        sid="S-1-5-21-1625922807-3304708894-3529444428-1001",
        **{"svm.uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
    )
    resource.delete()

```

---
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


__all__ = ["LocalCifsUser", "LocalCifsUserSchema"]
__pdoc__ = {
    "LocalCifsUserSchema.resource": False,
    "LocalCifsUser.local_cifs_user_show": False,
    "LocalCifsUser.local_cifs_user_create": False,
    "LocalCifsUser.local_cifs_user_modify": False,
    "LocalCifsUser.local_cifs_user_delete": False,
}


class LocalCifsUserSchema(ResourceSchema):
    """The fields of the LocalCifsUser object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the local_cifs_user. """

    account_disabled = fields.Boolean(
        data_key="account_disabled",
    )
    r""" Indicates whether the user account is enabled or disabled. """

    description = fields.Str(
        data_key="description",
        validate=len_validation(minimum=0, maximum=256),
    )
    r""" Description for the local user.


Example: This is local user. """

    full_name = fields.Str(
        data_key="full_name",
        validate=len_validation(minimum=0, maximum=256),
    )
    r""" User's full name.


Example: user name """

    membership = fields.List(fields.Nested("netapp_ontap.models.local_user_membership.LocalUserMembershipSchema", unknown=EXCLUDE), data_key="membership")
    r""" Specifies local groups of which this local user is a member. """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=1),
    )
    r""" Local user name. The maximum supported length of an user name is 20 characters.


Example: SMB_SERVER01\user """

    password = fields.Str(
        data_key="password",
        validate=len_validation(minimum=6),
    )
    r""" Password for the local user. """

    sid = fields.Str(
        data_key="sid",
    )
    r""" The security ID of the local user which uniquely identifies the user. The user SID is automatically generated in POST and it is retrieved using the GET method.


Example: S-1-5-21-256008430-3394229847-3930036330-1001 """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the local_cifs_user. """

    @property
    def resource(self):
        return LocalCifsUser

    gettable_fields = [
        "links",
        "account_disabled",
        "description",
        "full_name",
        "membership",
        "name",
        "sid",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,account_disabled,description,full_name,membership,name,sid,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "account_disabled",
        "description",
        "full_name",
        "name",
        "password",
        "svm.name",
        "svm.uuid",
    ]
    """account_disabled,description,full_name,name,password,svm.name,svm.uuid,"""

    postable_fields = [
        "account_disabled",
        "description",
        "full_name",
        "name",
        "password",
        "svm.name",
        "svm.uuid",
    ]
    """account_disabled,description,full_name,name,password,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in LocalCifsUser.get_collection(fields=field)]
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
            raise NetAppRestError("LocalCifsUser modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class LocalCifsUser(Resource):
    """Allows interaction with LocalCifsUser objects on the host"""

    _schema = LocalCifsUserSchema
    _path = "/api/protocols/cifs/local-users"
    _keys = ["svm.uuid", "sid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves local users for all of the SVMs. Local groups to which this user belongs to are also displayed.
### Advanced properties
* `membership`
### Related ONTAP commands
* `vserver cifs users-and-groups local-user show`
* `vserver cifs users-and-groups local-user show-membership`
### Learn more
* [`DOC /protocols/cifs/local-users`](#docs-NAS-protocols_cifs_local-users)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local cifs user show")
        def local_cifs_user_show(
            fields: List[Choices.define(["account_disabled", "description", "full_name", "name", "password", "sid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of LocalCifsUser resources

            Args:
                account_disabled: Indicates whether the user account is enabled or disabled. 
                description: Description for the local user. 
                full_name: User's full name. 
                name: Local user name. The maximum supported length of an user name is 20 characters. 
                password: Password for the local user. 
                sid: The security ID of the local user which uniquely identifies the user. The user SID is automatically generated in POST and it is retrieved using the GET method. 
            """

            kwargs = {}
            if account_disabled is not None:
                kwargs["account_disabled"] = account_disabled
            if description is not None:
                kwargs["description"] = description
            if full_name is not None:
                kwargs["full_name"] = full_name
            if name is not None:
                kwargs["name"] = name
            if password is not None:
                kwargs["password"] = password
            if sid is not None:
                kwargs["sid"] = sid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return LocalCifsUser.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all LocalCifsUser resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["LocalCifsUser"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates local user information for the specified user and SVM. The PATCH endpoint is also used to rename a user and to set the password for the user.
### Related ONTAP commands
* `vserver cifs users-and-groups local-user modify`
* `vserver cifs users-and-groups local-user rename`
* `vserver cifs users-and-groups local-user set-password`
### Learn more
* [`DOC /protocols/cifs/local-users`](#docs-NAS-protocols_cifs_local-users)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["LocalCifsUser"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["LocalCifsUser"], NetAppResponse]:
        r"""Creates the local user configuration for an SVM.<br/>
### Important notes
* The user name can contain up to 20 characters.
* The user name cannot be terminated by a period.
* The user name does not support any of the following characters: \" / ? [ ] , : | < > + = ; ? * @ or ASCII characters in the range 1-31.
* The password must be at least six characters in length and must not contain the user account name.
* The password must contain characters from three of the following four categories:
  - English uppercase characters (A through Z)
  - English lowercase characters (a through z)
  - Base 10 digits (0 through 9)
  - Special characters: ~ ! @ \# 0 ^ & * _ - + = ` ? | ( ) [ ] : ; \" \' < > , . ? /
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the local user.
* `name` - Name of the local user.
* `password` - Password for the local user.
### Default property values
If not specified in POST, the following default property value is assigned:
* `account_disabled` - false
### Related ONTAP commands
* `vserver cifs users-and-groups local-user create`
### Learn more
* [`DOC /protocols/cifs/local-users`](#docs-NAS-protocols_cifs_local-users)
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
        records: Iterable["LocalCifsUser"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a local user configuration for the specified SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups local-user delete`
### Learn more
* [`DOC /protocols/cifs/local-users`](#docs-NAS-protocols_cifs_local-users)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves local users for all of the SVMs. Local groups to which this user belongs to are also displayed.
### Advanced properties
* `membership`
### Related ONTAP commands
* `vserver cifs users-and-groups local-user show`
* `vserver cifs users-and-groups local-user show-membership`
### Learn more
* [`DOC /protocols/cifs/local-users`](#docs-NAS-protocols_cifs_local-users)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves local user information for the specified user and SVM.
### Advanced properties
* `membership`
### Related ONTAP commands
* `vserver cifs users-and-groups local-user show`
* `vserver cifs users-and-groups local-user show-membership`
### Learn more
* [`DOC /protocols/cifs/local-users`](#docs-NAS-protocols_cifs_local-users)
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
        r"""Creates the local user configuration for an SVM.<br/>
### Important notes
* The user name can contain up to 20 characters.
* The user name cannot be terminated by a period.
* The user name does not support any of the following characters: \" / ? [ ] , : | < > + = ; ? * @ or ASCII characters in the range 1-31.
* The password must be at least six characters in length and must not contain the user account name.
* The password must contain characters from three of the following four categories:
  - English uppercase characters (A through Z)
  - English lowercase characters (a through z)
  - Base 10 digits (0 through 9)
  - Special characters: ~ ! @ \# 0 ^ & * _ - + = ` ? | ( ) [ ] : ; \" \' < > , . ? /
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the local user.
* `name` - Name of the local user.
* `password` - Password for the local user.
### Default property values
If not specified in POST, the following default property value is assigned:
* `account_disabled` - false
### Related ONTAP commands
* `vserver cifs users-and-groups local-user create`
### Learn more
* [`DOC /protocols/cifs/local-users`](#docs-NAS-protocols_cifs_local-users)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local cifs user create")
        async def local_cifs_user_create(
        ) -> ResourceTable:
            """Create an instance of a LocalCifsUser resource

            Args:
                links: 
                account_disabled: Indicates whether the user account is enabled or disabled. 
                description: Description for the local user. 
                full_name: User's full name. 
                membership: Specifies local groups of which this local user is a member. 
                name: Local user name. The maximum supported length of an user name is 20 characters. 
                password: Password for the local user. 
                sid: The security ID of the local user which uniquely identifies the user. The user SID is automatically generated in POST and it is retrieved using the GET method. 
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if account_disabled is not None:
                kwargs["account_disabled"] = account_disabled
            if description is not None:
                kwargs["description"] = description
            if full_name is not None:
                kwargs["full_name"] = full_name
            if membership is not None:
                kwargs["membership"] = membership
            if name is not None:
                kwargs["name"] = name
            if password is not None:
                kwargs["password"] = password
            if sid is not None:
                kwargs["sid"] = sid
            if svm is not None:
                kwargs["svm"] = svm

            resource = LocalCifsUser(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create LocalCifsUser: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates local user information for the specified user and SVM. The PATCH endpoint is also used to rename a user and to set the password for the user.
### Related ONTAP commands
* `vserver cifs users-and-groups local-user modify`
* `vserver cifs users-and-groups local-user rename`
* `vserver cifs users-and-groups local-user set-password`
### Learn more
* [`DOC /protocols/cifs/local-users`](#docs-NAS-protocols_cifs_local-users)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local cifs user modify")
        async def local_cifs_user_modify(
        ) -> ResourceTable:
            """Modify an instance of a LocalCifsUser resource

            Args:
                account_disabled: Indicates whether the user account is enabled or disabled. 
                query_account_disabled: Indicates whether the user account is enabled or disabled. 
                description: Description for the local user. 
                query_description: Description for the local user. 
                full_name: User's full name. 
                query_full_name: User's full name. 
                name: Local user name. The maximum supported length of an user name is 20 characters. 
                query_name: Local user name. The maximum supported length of an user name is 20 characters. 
                password: Password for the local user. 
                query_password: Password for the local user. 
                sid: The security ID of the local user which uniquely identifies the user. The user SID is automatically generated in POST and it is retrieved using the GET method. 
                query_sid: The security ID of the local user which uniquely identifies the user. The user SID is automatically generated in POST and it is retrieved using the GET method. 
            """

            kwargs = {}
            changes = {}
            if query_account_disabled is not None:
                kwargs["account_disabled"] = query_account_disabled
            if query_description is not None:
                kwargs["description"] = query_description
            if query_full_name is not None:
                kwargs["full_name"] = query_full_name
            if query_name is not None:
                kwargs["name"] = query_name
            if query_password is not None:
                kwargs["password"] = query_password
            if query_sid is not None:
                kwargs["sid"] = query_sid

            if account_disabled is not None:
                changes["account_disabled"] = account_disabled
            if description is not None:
                changes["description"] = description
            if full_name is not None:
                changes["full_name"] = full_name
            if name is not None:
                changes["name"] = name
            if password is not None:
                changes["password"] = password
            if sid is not None:
                changes["sid"] = sid

            if hasattr(LocalCifsUser, "find"):
                resource = LocalCifsUser.find(
                    **kwargs
                )
            else:
                resource = LocalCifsUser()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify LocalCifsUser: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a local user configuration for the specified SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups local-user delete`
### Learn more
* [`DOC /protocols/cifs/local-users`](#docs-NAS-protocols_cifs_local-users)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="local cifs user delete")
        async def local_cifs_user_delete(
        ) -> None:
            """Delete an instance of a LocalCifsUser resource

            Args:
                account_disabled: Indicates whether the user account is enabled or disabled. 
                description: Description for the local user. 
                full_name: User's full name. 
                name: Local user name. The maximum supported length of an user name is 20 characters. 
                password: Password for the local user. 
                sid: The security ID of the local user which uniquely identifies the user. The user SID is automatically generated in POST and it is retrieved using the GET method. 
            """

            kwargs = {}
            if account_disabled is not None:
                kwargs["account_disabled"] = account_disabled
            if description is not None:
                kwargs["description"] = description
            if full_name is not None:
                kwargs["full_name"] = full_name
            if name is not None:
                kwargs["name"] = name
            if password is not None:
                kwargs["password"] = password
            if sid is not None:
                kwargs["sid"] = sid

            if hasattr(LocalCifsUser, "find"):
                resource = LocalCifsUser.find(
                    **kwargs
                )
            else:
                resource = LocalCifsUser()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete LocalCifsUser: %s" % err)


