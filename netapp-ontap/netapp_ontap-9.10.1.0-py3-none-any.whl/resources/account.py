r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
This API displays and manages the configuration of scoped user accounts.<p/>
Newly created user accounts might need to be updated for many reasons. For example, a user account might need to use a different application or its role might need to be modified. According to a policy, the password or authentication source of a user account might need to be changed, or a user account might need to be locked or deleted from the system. This API allows you to make these changes to user accounts.<p/>
Specify the owner UUID and the user account name in the URI path. The owner UUID corresponds to the UUID of the SVM for which the user account has been created and can be obtained from the response body of the GET request performed on one of the following APIs:
<i>/api/security/accounts</i> for all user accounts
<i>/api/security/accounts/?scope=cluster</i> for cluster-scoped user accounts
<i>/api/security/accounts/?scope=svm</i> for SVM-scoped accounts
<i>/api/security/accounts/?owner.name=<svm-name></i> for a specific SVM
This API response contains the complete URI for each user account that can be used.
## Examples
### Retrieving the user account details
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Account

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Account(
        name="svm_user1", **{"owner.uuid": "aef7c38-4bd3-11e9-b238-0050568e2e25"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
Account(
    {
        "role": {
            "name": "vsadmin",
            "_links": {
                "self": {
                    "href": "/api/svms/aaef7c38-4bd3-11e9-b238-0050568e2e25/admin/roles/vsadmin"
                }
            },
        },
        "owner": {
            "_links": {
                "self": {"href": "/api/svm/svms/aaef7c38-4bd3-11e9-b238-0050568e2e25"}
            },
            "uuid": "aaef7c38-4bd3-11e9-b238-0050568e2e25",
            "name": "svm1",
        },
        "applications": [
            {
                "application": "ssh",
                "second_authentication_method": "none",
                "authentication_methods": ["password"],
            }
        ],
        "scope": "svm",
        "locked": False,
        "name": "svm_user1",
        "_links": {
            "self": {
                "href": "/api/security/accounts/aaef7c38-4bd3-11e9-b238-0050568e2e25/svm_user1"
            }
        },
    }
)

```
</div>
</div>

### Updating the applications and role in a user account
Specify the desired configuration in the form of tuples (of applications and authentication methods) and the role. All other previously configured applications that are not specified in the "applications" parameter of the PATCH request will be de-provisioned for the user account.<p/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Account

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Account(
        name="svm_user1", **{"owner.uuid": "aaef7c38-4bd3-11e9-b238-0050568e2e25"}
    )
    resource.applications = [
        {"application": "http", "authentication_methods": ["domain"]},
        {"application": "ontapi", "authentication_methods": ["password"]},
    ]
    resource.role = {"name": "vsadmin-backup"}
    resource.patch()

```

### Updating the password for a user account
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Account

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Account(
        name="svm_user1", **{"owner.uuid": "aaef7c38-4bd3-11e9-b238-0050568e2e25"}
    )
    resource.password = "newp@ssw@rd2"
    resource.patch()

```

### Locking a user account
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Account

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Account(
        name="svm_user1", **{"owner.uuid": "aaef7c38-4bd3-11e9-b238-0050568e2e25"}
    )
    resource.locked = True
    resource.patch()

```

### Deleting a user account
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Account

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Account(
        name="svm_user1", **{"owner.uuid": "aaef7c38-4bd3-11e9-b238-0050568e2e25"}
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


__all__ = ["Account", "AccountSchema"]
__pdoc__ = {
    "AccountSchema.resource": False,
    "Account.account_show": False,
    "Account.account_create": False,
    "Account.account_modify": False,
    "Account.account_delete": False,
}


class AccountSchema(ResourceSchema):
    """The fields of the Account object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the account. """

    applications = fields.List(fields.Nested("netapp_ontap.models.account_application.AccountApplicationSchema", unknown=EXCLUDE), data_key="applications")
    r""" The applications field of the account. """

    comment = fields.Str(
        data_key="comment",
    )
    r""" Optional comment for the user account. """

    locked = fields.Boolean(
        data_key="locked",
    )
    r""" Locked status of the account. """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=3, maximum=64),
    )
    r""" User or group account name

Example: joe.smith """

    owner = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="owner", unknown=EXCLUDE)
    r""" The owner field of the account. """

    password = fields.Str(
        data_key="password",
        validate=len_validation(minimum=8, maximum=128),
    )
    r""" Password for the account. The password can contain a mix of lower and upper case alphabetic characters, digits, and special characters. """

    role = fields.Nested("netapp_ontap.resources.role.RoleSchema", data_key="role", unknown=EXCLUDE)
    r""" The role field of the account. """

    scope = fields.Str(
        data_key="scope",
        validate=enum_validation(['cluster', 'svm']),
    )
    r""" Scope of the entity. Set to "cluster" for cluster owned objects and to "svm" for SVM owned objects.

Valid choices:

* cluster
* svm """

    @property
    def resource(self):
        return Account

    gettable_fields = [
        "links",
        "applications",
        "comment",
        "locked",
        "name",
        "owner.links",
        "owner.name",
        "owner.uuid",
        "role.links",
        "role.name",
        "scope",
    ]
    """links,applications,comment,locked,name,owner.links,owner.name,owner.uuid,role.links,role.name,scope,"""

    patchable_fields = [
        "applications",
        "comment",
        "locked",
        "password",
        "role.name",
    ]
    """applications,comment,locked,password,role.name,"""

    postable_fields = [
        "applications",
        "comment",
        "locked",
        "name",
        "owner.name",
        "owner.uuid",
        "password",
        "role.name",
    ]
    """applications,comment,locked,name,owner.name,owner.uuid,password,role.name,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Account.get_collection(fields=field)]
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
            raise NetAppRestError("Account modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Account(Resource):
    """Allows interaction with Account objects on the host"""

    _schema = AccountSchema
    _path = "/api/security/accounts"
    _keys = ["owner.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a list of user accounts in the cluster.
### Related ONTAP commands
* `security login show`
### Learn more
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="account show")
        def account_show(
            fields: List[Choices.define(["comment", "locked", "name", "password", "scope", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of Account resources

            Args:
                comment: Optional comment for the user account.
                locked: Locked status of the account.
                name: User or group account name
                password: Password for the account. The password can contain a mix of lower and upper case alphabetic characters, digits, and special characters.
                scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if locked is not None:
                kwargs["locked"] = locked
            if name is not None:
                kwargs["name"] = name
            if password is not None:
                kwargs["password"] = password
            if scope is not None:
                kwargs["scope"] = scope
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return Account.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Account resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["Account"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a user account. Locks or unlocks a user account and/or updates the role, applications, and/or password for the user account.
### Required parameters
* `name` - Account name to be updated.
* `owner.uuid`  - UUID of the SVM housing the user account to be updated.
### Optional parameters
* `applications` - Array of one or more tuples (of application and authentication methods).
* `role` - RBAC role for the user account.
* `password` - Password for the user account (if the authentication method is opted as password for one or more of applications).
* `second_authentication_method` - Needed for MFA and only supported for ssh application. Defaults to `none` if not supplied.
* `comment` - Comment for the user account (e.g purpose of this account).
* `locked` - Set to true/false to lock/unlock the account.
### Related ONTAP commands
* `security login create`
* `security login modify`
* `security login password`
* `security login lock`
* `security login unlock`
### Learn more
* [`DOC /security/accounts/{owner.uuid}/{name}`](#docs-security-security_accounts_{owner.uuid}_{name})
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["Account"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["Account"], NetAppResponse]:
        r"""Creates a new user account.
### Required parameters
* `name` - Account name to be created.
* `applications` - Array of one or more application tuples (of application and authentication methods).
### Optional parameters
* `owner.name` or `owner.uuid`  - Name or UUID of the SVM for an SVM-scoped user account. If not supplied, a cluster-scoped user account is created.
* `role` - RBAC role for the user account. Defaulted to `admin` for cluster user account and to `vsadmin` for SVM-scoped account.
* `password` - Password for the user account (if the authentication method is opted as password for one or more of applications).
* `second_authentication_method` - Needed for MFA and only supported for ssh application. Defaults to `none` if not supplied.
* `comment` - Comment for the user account (e.g purpose of this account).
* `locked` - Locks the account after creation. Defaults to `false` if not supplied.
### Related ONTAP commands
* `security login create`
### Learn more
* [`DOC /security/accounts`](#docs-security-security_accounts)
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
        records: Iterable["Account"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a user account.
### Required parameters
* `name` - Account name to be deleted.
* `owner.uuid`  - UUID of the SVM housing the user account to be deleted.
### Related ONTAP commands
* `security login delete`
### Learn more
* [`DOC /security/accounts/{owner.uuid}/{name}`](#docs-security-security_accounts_{owner.uuid}_{name})
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a list of user accounts in the cluster.
### Related ONTAP commands
* `security login show`
### Learn more
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific user account.
### Related ONTAP commands
* `security login show`
### Learn more
* [`DOC /security/accounts/{owner.uuid}/{name}`](#docs-security-security_accounts_{owner.uuid}_{name})
* [`DOC /security/accounts`](#docs-security-security_accounts)
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
        r"""Creates a new user account.
### Required parameters
* `name` - Account name to be created.
* `applications` - Array of one or more application tuples (of application and authentication methods).
### Optional parameters
* `owner.name` or `owner.uuid`  - Name or UUID of the SVM for an SVM-scoped user account. If not supplied, a cluster-scoped user account is created.
* `role` - RBAC role for the user account. Defaulted to `admin` for cluster user account and to `vsadmin` for SVM-scoped account.
* `password` - Password for the user account (if the authentication method is opted as password for one or more of applications).
* `second_authentication_method` - Needed for MFA and only supported for ssh application. Defaults to `none` if not supplied.
* `comment` - Comment for the user account (e.g purpose of this account).
* `locked` - Locks the account after creation. Defaults to `false` if not supplied.
### Related ONTAP commands
* `security login create`
### Learn more
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="account create")
        async def account_create(
        ) -> ResourceTable:
            """Create an instance of a Account resource

            Args:
                links: 
                applications: 
                comment: Optional comment for the user account.
                locked: Locked status of the account.
                name: User or group account name
                owner: 
                password: Password for the account. The password can contain a mix of lower and upper case alphabetic characters, digits, and special characters.
                role: 
                scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if applications is not None:
                kwargs["applications"] = applications
            if comment is not None:
                kwargs["comment"] = comment
            if locked is not None:
                kwargs["locked"] = locked
            if name is not None:
                kwargs["name"] = name
            if owner is not None:
                kwargs["owner"] = owner
            if password is not None:
                kwargs["password"] = password
            if role is not None:
                kwargs["role"] = role
            if scope is not None:
                kwargs["scope"] = scope

            resource = Account(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create Account: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a user account. Locks or unlocks a user account and/or updates the role, applications, and/or password for the user account.
### Required parameters
* `name` - Account name to be updated.
* `owner.uuid`  - UUID of the SVM housing the user account to be updated.
### Optional parameters
* `applications` - Array of one or more tuples (of application and authentication methods).
* `role` - RBAC role for the user account.
* `password` - Password for the user account (if the authentication method is opted as password for one or more of applications).
* `second_authentication_method` - Needed for MFA and only supported for ssh application. Defaults to `none` if not supplied.
* `comment` - Comment for the user account (e.g purpose of this account).
* `locked` - Set to true/false to lock/unlock the account.
### Related ONTAP commands
* `security login create`
* `security login modify`
* `security login password`
* `security login lock`
* `security login unlock`
### Learn more
* [`DOC /security/accounts/{owner.uuid}/{name}`](#docs-security-security_accounts_{owner.uuid}_{name})
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="account modify")
        async def account_modify(
        ) -> ResourceTable:
            """Modify an instance of a Account resource

            Args:
                comment: Optional comment for the user account.
                query_comment: Optional comment for the user account.
                locked: Locked status of the account.
                query_locked: Locked status of the account.
                name: User or group account name
                query_name: User or group account name
                password: Password for the account. The password can contain a mix of lower and upper case alphabetic characters, digits, and special characters.
                query_password: Password for the account. The password can contain a mix of lower and upper case alphabetic characters, digits, and special characters.
                scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
                query_scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
            """

            kwargs = {}
            changes = {}
            if query_comment is not None:
                kwargs["comment"] = query_comment
            if query_locked is not None:
                kwargs["locked"] = query_locked
            if query_name is not None:
                kwargs["name"] = query_name
            if query_password is not None:
                kwargs["password"] = query_password
            if query_scope is not None:
                kwargs["scope"] = query_scope

            if comment is not None:
                changes["comment"] = comment
            if locked is not None:
                changes["locked"] = locked
            if name is not None:
                changes["name"] = name
            if password is not None:
                changes["password"] = password
            if scope is not None:
                changes["scope"] = scope

            if hasattr(Account, "find"):
                resource = Account.find(
                    **kwargs
                )
            else:
                resource = Account()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify Account: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a user account.
### Required parameters
* `name` - Account name to be deleted.
* `owner.uuid`  - UUID of the SVM housing the user account to be deleted.
### Related ONTAP commands
* `security login delete`
### Learn more
* [`DOC /security/accounts/{owner.uuid}/{name}`](#docs-security-security_accounts_{owner.uuid}_{name})
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="account delete")
        async def account_delete(
        ) -> None:
            """Delete an instance of a Account resource

            Args:
                comment: Optional comment for the user account.
                locked: Locked status of the account.
                name: User or group account name
                password: Password for the account. The password can contain a mix of lower and upper case alphabetic characters, digits, and special characters.
                scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if locked is not None:
                kwargs["locked"] = locked
            if name is not None:
                kwargs["name"] = name
            if password is not None:
                kwargs["password"] = password
            if scope is not None:
                kwargs["scope"] = scope

            if hasattr(Account, "find"):
                resource = Account.find(
                    **kwargs
                )
            else:
                resource = Account()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete Account: %s" % err)


