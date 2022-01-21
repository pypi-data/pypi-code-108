r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
This API configures the public keys for end-user (non-cluster admin) accounts.
Specify the owner UUID, the user account name, and the index in the URI path. The owner UUID corresponds to the UUID of the SVM containing the user account associated with the public key and can be obtained from the response body of the GET request performed on the API “/api/svm/svms".<br/> The index value corresponds to the public key that needs to be modified or deleted (it is possible to create more than one public key for the same user account).
## Examples
### Retrieving the specific configured public key for user accounts
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Publickey

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Publickey(
        index=0,
        **{
            "account.name": "pubuser4",
            "owner.uuid": "513a78c7-8c13-11e9-8f78-005056bbf6ac",
        }
    )
    resource.get()
    print(resource)

```

### Updating the public key and comment for user accounts
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Publickey

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Publickey(
        index=0,
        **{
            "account.name": "pubuser1",
            "owner.uuid": "d49de271-8c11-11e9-8f78-005056bbf6ac",
        }
    )
    resource.comment = "Cserver-modification"
    resource.public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCmSLP/FeiT1J4Fb4GNVO4ioa1NIUHWeG08+anDbFke3JcFT5JqBn0QZiG0uF0bqepken/moVKZg8iQng1arjP4ULhhje/LwDuUbaB7kvtPL2gyzAX1qFYnBJ5R1LXja25Z4xeeaXUBJjhUmvpfque0TxbvpaG5V9rFTzVg9ccjBnkBchg3EkhF4VtHmrZNpTDAUOBAz69FRYXYz2ExoCHWqElHBJep9D0DLN0XtzQA0IF9hJck6xja5RcAQ6f9pLMCol9vJiqpcBAjkUmg1qH5ZNHsgDQ7dtGNGJw45zqXHPAy9z8yKJuIsdK2/4iVYLDL8mlHFElgeADn6OSxuij1"
    resource.patch()

```

### Deleting the public key for user accounts
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Publickey

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Publickey(
        index=0,
        **{
            "account.name": "pubuser1",
            "owner.uuid": "d49de271-8c11-11e9-8f78-005056bbf6ac",
        }
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


__all__ = ["Publickey", "PublickeySchema"]
__pdoc__ = {
    "PublickeySchema.resource": False,
    "Publickey.publickey_show": False,
    "Publickey.publickey_create": False,
    "Publickey.publickey_modify": False,
    "Publickey.publickey_delete": False,
}


class PublickeySchema(ResourceSchema):
    """The fields of the Publickey object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the publickey. """

    account = fields.Nested("netapp_ontap.resources.account.AccountSchema", data_key="account", unknown=EXCLUDE)
    r""" The account field of the publickey. """

    comment = fields.Str(
        data_key="comment",
    )
    r""" Optional comment for the public key. """

    index = Size(
        data_key="index",
        validate=integer_validation(minimum=0, maximum=99),
    )
    r""" Index number for the public key (where there are multiple keys for the same account). """

    obfuscated_fingerprint = fields.Str(
        data_key="obfuscated_fingerprint",
    )
    r""" The obfuscated fingerprint for the public key (READONLY). """

    owner = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="owner", unknown=EXCLUDE)
    r""" The owner field of the publickey. """

    public_key = fields.Str(
        data_key="public_key",
    )
    r""" The public key """

    scope = fields.Str(
        data_key="scope",
        validate=enum_validation(['cluster', 'svm']),
    )
    r""" Scope of the entity. Set to "cluster" for cluster owned objects and to "svm" for SVM owned objects.

Valid choices:

* cluster
* svm """

    sha_fingerprint = fields.Str(
        data_key="sha_fingerprint",
    )
    r""" The SHA fingerprint for the public key (READONLY). """

    @property
    def resource(self):
        return Publickey

    gettable_fields = [
        "links",
        "account.links",
        "account.name",
        "comment",
        "index",
        "obfuscated_fingerprint",
        "owner.links",
        "owner.name",
        "owner.uuid",
        "public_key",
        "scope",
        "sha_fingerprint",
    ]
    """links,account.links,account.name,comment,index,obfuscated_fingerprint,owner.links,owner.name,owner.uuid,public_key,scope,sha_fingerprint,"""

    patchable_fields = [
        "account.name",
        "comment",
        "public_key",
    ]
    """account.name,comment,public_key,"""

    postable_fields = [
        "account.name",
        "comment",
        "index",
        "owner.name",
        "owner.uuid",
        "public_key",
    ]
    """account.name,comment,index,owner.name,owner.uuid,public_key,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Publickey.get_collection(fields=field)]
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
            raise NetAppRestError("Publickey modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Publickey(Resource):
    r""" The public key for the user account (to access SSH). """

    _schema = PublickeySchema
    _path = "/api/security/authentication/publickeys"
    _keys = ["owner.uuid", "account.name", "index"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the public keys configured for user accounts.
### Related ONTAP commands
* `security login publickey show`
### Learn more
* [`DOC /security/authentication/publickeys`](#docs-security-security_authentication_publickeys)
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="publickey show")
        def publickey_show(
            fields: List[Choices.define(["comment", "index", "obfuscated_fingerprint", "public_key", "scope", "sha_fingerprint", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of Publickey resources

            Args:
                comment: Optional comment for the public key.
                index: Index number for the public key (where there are multiple keys for the same account).
                obfuscated_fingerprint: The obfuscated fingerprint for the public key (READONLY).
                public_key: The public key
                scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
                sha_fingerprint: The SHA fingerprint for the public key (READONLY).
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if index is not None:
                kwargs["index"] = index
            if obfuscated_fingerprint is not None:
                kwargs["obfuscated_fingerprint"] = obfuscated_fingerprint
            if public_key is not None:
                kwargs["public_key"] = public_key
            if scope is not None:
                kwargs["scope"] = scope
            if sha_fingerprint is not None:
                kwargs["sha_fingerprint"] = sha_fingerprint
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return Publickey.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Publickey resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["Publickey"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the public key for a user account.
### Related ONTAP commands
* `security login publickey modify`
### Learn more
* [`DOC /security/authentication/publickeys/{owner.uuid}/{account.name}/{index}`](#docs-security-security_authentication_publickeys_{owner.uuid}_{account.name}_{index})
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
        records: Iterable["Publickey"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["Publickey"], NetAppResponse]:
        r"""Creates a public key for a user account.
### Required properties
* `owner.uuid` - UUID of the account owner.
* `name` - User account name.
* `index` - Index number for the public key (where there are multiple keys for the same account).
* `public_key` - The publickey details for the creation of the user account.
### Related ONTAP commands
* `security login publickey create`
### Learn more
* [`DOC /security/authentication/publickeys`](#docs-security-security_authentication_publickeys)
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
        records: Iterable["Publickey"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the public key for a user account.
### Related ONTAP commands
* `security login publickey delete`
### Learn more
* [`DOC /security/authentication/publickeys/{owner.uuid}/{account.name}/{index}`](#docs-security-security_authentication_publickeys_{owner.uuid}_{account.name}_{index})
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the public keys configured for user accounts.
### Related ONTAP commands
* `security login publickey show`
### Learn more
* [`DOC /security/authentication/publickeys`](#docs-security-security_authentication_publickeys)
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the public keys configured for a user account.
### Related ONTAP commands
* `security login publickey show`
### Learn more
* [`DOC /security/authentication/publickeys/{owner.uuid}/{account.name}/{index}`](#docs-security-security_authentication_publickeys_{owner.uuid}_{account.name}_{index})
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
        r"""Creates a public key for a user account.
### Required properties
* `owner.uuid` - UUID of the account owner.
* `name` - User account name.
* `index` - Index number for the public key (where there are multiple keys for the same account).
* `public_key` - The publickey details for the creation of the user account.
### Related ONTAP commands
* `security login publickey create`
### Learn more
* [`DOC /security/authentication/publickeys`](#docs-security-security_authentication_publickeys)
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="publickey create")
        async def publickey_create(
        ) -> ResourceTable:
            """Create an instance of a Publickey resource

            Args:
                links: 
                account: 
                comment: Optional comment for the public key.
                index: Index number for the public key (where there are multiple keys for the same account).
                obfuscated_fingerprint: The obfuscated fingerprint for the public key (READONLY).
                owner: 
                public_key: The public key
                scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
                sha_fingerprint: The SHA fingerprint for the public key (READONLY).
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if account is not None:
                kwargs["account"] = account
            if comment is not None:
                kwargs["comment"] = comment
            if index is not None:
                kwargs["index"] = index
            if obfuscated_fingerprint is not None:
                kwargs["obfuscated_fingerprint"] = obfuscated_fingerprint
            if owner is not None:
                kwargs["owner"] = owner
            if public_key is not None:
                kwargs["public_key"] = public_key
            if scope is not None:
                kwargs["scope"] = scope
            if sha_fingerprint is not None:
                kwargs["sha_fingerprint"] = sha_fingerprint

            resource = Publickey(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create Publickey: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the public key for a user account.
### Related ONTAP commands
* `security login publickey modify`
### Learn more
* [`DOC /security/authentication/publickeys/{owner.uuid}/{account.name}/{index}`](#docs-security-security_authentication_publickeys_{owner.uuid}_{account.name}_{index})
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="publickey modify")
        async def publickey_modify(
        ) -> ResourceTable:
            """Modify an instance of a Publickey resource

            Args:
                comment: Optional comment for the public key.
                query_comment: Optional comment for the public key.
                index: Index number for the public key (where there are multiple keys for the same account).
                query_index: Index number for the public key (where there are multiple keys for the same account).
                obfuscated_fingerprint: The obfuscated fingerprint for the public key (READONLY).
                query_obfuscated_fingerprint: The obfuscated fingerprint for the public key (READONLY).
                public_key: The public key
                query_public_key: The public key
                scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
                query_scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
                sha_fingerprint: The SHA fingerprint for the public key (READONLY).
                query_sha_fingerprint: The SHA fingerprint for the public key (READONLY).
            """

            kwargs = {}
            changes = {}
            if query_comment is not None:
                kwargs["comment"] = query_comment
            if query_index is not None:
                kwargs["index"] = query_index
            if query_obfuscated_fingerprint is not None:
                kwargs["obfuscated_fingerprint"] = query_obfuscated_fingerprint
            if query_public_key is not None:
                kwargs["public_key"] = query_public_key
            if query_scope is not None:
                kwargs["scope"] = query_scope
            if query_sha_fingerprint is not None:
                kwargs["sha_fingerprint"] = query_sha_fingerprint

            if comment is not None:
                changes["comment"] = comment
            if index is not None:
                changes["index"] = index
            if obfuscated_fingerprint is not None:
                changes["obfuscated_fingerprint"] = obfuscated_fingerprint
            if public_key is not None:
                changes["public_key"] = public_key
            if scope is not None:
                changes["scope"] = scope
            if sha_fingerprint is not None:
                changes["sha_fingerprint"] = sha_fingerprint

            if hasattr(Publickey, "find"):
                resource = Publickey.find(
                    **kwargs
                )
            else:
                resource = Publickey()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify Publickey: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the public key for a user account.
### Related ONTAP commands
* `security login publickey delete`
### Learn more
* [`DOC /security/authentication/publickeys/{owner.uuid}/{account.name}/{index}`](#docs-security-security_authentication_publickeys_{owner.uuid}_{account.name}_{index})
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="publickey delete")
        async def publickey_delete(
        ) -> None:
            """Delete an instance of a Publickey resource

            Args:
                comment: Optional comment for the public key.
                index: Index number for the public key (where there are multiple keys for the same account).
                obfuscated_fingerprint: The obfuscated fingerprint for the public key (READONLY).
                public_key: The public key
                scope: Scope of the entity. Set to \"cluster\" for cluster owned objects and to \"svm\" for SVM owned objects.
                sha_fingerprint: The SHA fingerprint for the public key (READONLY).
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if index is not None:
                kwargs["index"] = index
            if obfuscated_fingerprint is not None:
                kwargs["obfuscated_fingerprint"] = obfuscated_fingerprint
            if public_key is not None:
                kwargs["public_key"] = public_key
            if scope is not None:
                kwargs["scope"] = scope
            if sha_fingerprint is not None:
                kwargs["sha_fingerprint"] = sha_fingerprint

            if hasattr(Publickey, "find"):
                resource = Publickey.find(
                    **kwargs
                )
            else:
                resource = Publickey()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete Publickey: %s" % err)


