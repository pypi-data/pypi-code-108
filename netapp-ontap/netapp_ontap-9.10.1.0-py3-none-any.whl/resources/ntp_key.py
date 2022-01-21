r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
You can configure NTP to use shared private keys between ONTAP and trusted external NTP time servers.</br>
You acquire the keys from the external NTP time servers and individual entries created for each
unique key. You can use the /cluster/ntp/servers API to associate a key with an external NTP time server
used by ONTAP and enable authentication.
### Fields used for adding an NTP shared key
The required fields are:

* `id`
* `digest_type`
* `secret_key`
## Example
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NtpKey

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NtpKey()
    resource.id = 10
    resource.digest_type = "sha1"
    resource.value = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    resource.post(hydrate=True)
    print(resource)

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


__all__ = ["NtpKey", "NtpKeySchema"]
__pdoc__ = {
    "NtpKeySchema.resource": False,
    "NtpKey.ntp_key_show": False,
    "NtpKey.ntp_key_create": False,
    "NtpKey.ntp_key_modify": False,
    "NtpKey.ntp_key_delete": False,
}


class NtpKeySchema(ResourceSchema):
    """The fields of the NtpKey object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the ntp_key. """

    digest_type = fields.Str(
        data_key="digest_type",
        validate=enum_validation(['sha1']),
    )
    r""" The type of cryptographic hash used to create and verify the NTP's message authentication code appended to each NTP packet header.


Valid choices:

* sha1 """

    id = Size(
        data_key="id",
        validate=integer_validation(minimum=1, maximum=65535),
    )
    r""" NTP symmetric authentication key identifier or index number (ID). This ID is included
in the NTP cryptographic hash encoded header.


Example: 10 """

    value = fields.Str(
        data_key="value",
    )
    r""" A hexadecimal digit string that represents the cryptographic key that is shared with the remote NTP server.
The current expected length is 40 characters.
</br>
Use the cryptographic key and key ID to create a unique hash value used to authenticate the rest of the NTP data.


Example: da39a3ee5e6b4b0d3255bfef95601890afd80709 """

    @property
    def resource(self):
        return NtpKey

    gettable_fields = [
        "links",
        "digest_type",
        "id",
        "value",
    ]
    """links,digest_type,id,value,"""

    patchable_fields = [
        "digest_type",
        "value",
    ]
    """digest_type,value,"""

    postable_fields = [
        "digest_type",
        "id",
        "value",
    ]
    """digest_type,id,value,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NtpKey.get_collection(fields=field)]
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
            raise NetAppRestError("NtpKey modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NtpKey(Resource):
    """Allows interaction with NtpKey objects on the host"""

    _schema = NtpKeySchema
    _path = "/api/cluster/ntp/keys"
    _keys = ["id"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the collection of NTP symmetric authentication keys known by ONTAP that
are uniquely indexed by an identifier.
### Related ONTAP commands
* `cluster time-service ntp key show`
### Learn more
* [`DOC /cluster/ntp/keys`](#docs-cluster-cluster_ntp_keys)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ntp key show")
        def ntp_key_show(
            fields: List[Choices.define(["digest_type", "id", "value", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of NtpKey resources

            Args:
                digest_type: The type of cryptographic hash used to create and verify the NTP's message authentication code appended to each NTP packet header. 
                id: NTP symmetric authentication key identifier or index number (ID). This ID is included in the NTP cryptographic hash encoded header. 
                value: A hexadecimal digit string that represents the cryptographic key that is shared with the remote NTP server. The current expected length is 40 characters. </br> Use the cryptographic key and key ID to create a unique hash value used to authenticate the rest of the NTP data. 
            """

            kwargs = {}
            if digest_type is not None:
                kwargs["digest_type"] = digest_type
            if id is not None:
                kwargs["id"] = id
            if value is not None:
                kwargs["value"] = value
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return NtpKey.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NtpKey resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["NtpKey"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the details of a specific NTP symmetric authentication key by numeric
identifier or index (ID).
### Required properties
* `digest_type` - Shared private key cryptographic hash type.
* `value` - Value of shared private key.
### Related ONTAP commands
* `cluster time-service ntp key modify`
### Learn more
* [`DOC /cluster/ntp/keys`](#docs-cluster-cluster_ntp_keys)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["NtpKey"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["NtpKey"], NetAppResponse]:
        r"""Creates an NTP symmetric authentication key entry including the type of key
using an unused identifier or index number (ID).
### Required properties
* `id` - Shared symmetric key number (ID).
* `digest_type` - Shared private key cryptographic hash type.
* `value` - Value of shared private key.
### Related ONTAP commands
* `cluster time-service ntp key create`
### Learn more
* [`DOC /cluster/ntp/keys`](#docs-cluster-cluster_ntp_keys)
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
        records: Iterable["NtpKey"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an NTP key.
### Related ONTAP commands
* `cluster time-service ntp key delete`
### Learn more
* [`DOC /cluster/ntp/keys`](#docs-cluster-cluster_ntp_keys)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the collection of NTP symmetric authentication keys known by ONTAP that
are uniquely indexed by an identifier.
### Related ONTAP commands
* `cluster time-service ntp key show`
### Learn more
* [`DOC /cluster/ntp/keys`](#docs-cluster-cluster_ntp_keys)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the details of a specific NTP symmetric authentication key by numeric identifier or index (ID).
### Related ONTAP commands
* `cluster time-service ntp key show`
### Learn more
* [`DOC /cluster/ntp/keys`](#docs-cluster-cluster_ntp_keys)
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
        r"""Creates an NTP symmetric authentication key entry including the type of key
using an unused identifier or index number (ID).
### Required properties
* `id` - Shared symmetric key number (ID).
* `digest_type` - Shared private key cryptographic hash type.
* `value` - Value of shared private key.
### Related ONTAP commands
* `cluster time-service ntp key create`
### Learn more
* [`DOC /cluster/ntp/keys`](#docs-cluster-cluster_ntp_keys)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ntp key create")
        async def ntp_key_create(
        ) -> ResourceTable:
            """Create an instance of a NtpKey resource

            Args:
                links: 
                digest_type: The type of cryptographic hash used to create and verify the NTP's message authentication code appended to each NTP packet header. 
                id: NTP symmetric authentication key identifier or index number (ID). This ID is included in the NTP cryptographic hash encoded header. 
                value: A hexadecimal digit string that represents the cryptographic key that is shared with the remote NTP server. The current expected length is 40 characters. </br> Use the cryptographic key and key ID to create a unique hash value used to authenticate the rest of the NTP data. 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if digest_type is not None:
                kwargs["digest_type"] = digest_type
            if id is not None:
                kwargs["id"] = id
            if value is not None:
                kwargs["value"] = value

            resource = NtpKey(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create NtpKey: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the details of a specific NTP symmetric authentication key by numeric
identifier or index (ID).
### Required properties
* `digest_type` - Shared private key cryptographic hash type.
* `value` - Value of shared private key.
### Related ONTAP commands
* `cluster time-service ntp key modify`
### Learn more
* [`DOC /cluster/ntp/keys`](#docs-cluster-cluster_ntp_keys)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ntp key modify")
        async def ntp_key_modify(
        ) -> ResourceTable:
            """Modify an instance of a NtpKey resource

            Args:
                digest_type: The type of cryptographic hash used to create and verify the NTP's message authentication code appended to each NTP packet header. 
                query_digest_type: The type of cryptographic hash used to create and verify the NTP's message authentication code appended to each NTP packet header. 
                id: NTP symmetric authentication key identifier or index number (ID). This ID is included in the NTP cryptographic hash encoded header. 
                query_id: NTP symmetric authentication key identifier or index number (ID). This ID is included in the NTP cryptographic hash encoded header. 
                value: A hexadecimal digit string that represents the cryptographic key that is shared with the remote NTP server. The current expected length is 40 characters. </br> Use the cryptographic key and key ID to create a unique hash value used to authenticate the rest of the NTP data. 
                query_value: A hexadecimal digit string that represents the cryptographic key that is shared with the remote NTP server. The current expected length is 40 characters. </br> Use the cryptographic key and key ID to create a unique hash value used to authenticate the rest of the NTP data. 
            """

            kwargs = {}
            changes = {}
            if query_digest_type is not None:
                kwargs["digest_type"] = query_digest_type
            if query_id is not None:
                kwargs["id"] = query_id
            if query_value is not None:
                kwargs["value"] = query_value

            if digest_type is not None:
                changes["digest_type"] = digest_type
            if id is not None:
                changes["id"] = id
            if value is not None:
                changes["value"] = value

            if hasattr(NtpKey, "find"):
                resource = NtpKey.find(
                    **kwargs
                )
            else:
                resource = NtpKey()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify NtpKey: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an NTP key.
### Related ONTAP commands
* `cluster time-service ntp key delete`
### Learn more
* [`DOC /cluster/ntp/keys`](#docs-cluster-cluster_ntp_keys)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ntp key delete")
        async def ntp_key_delete(
        ) -> None:
            """Delete an instance of a NtpKey resource

            Args:
                digest_type: The type of cryptographic hash used to create and verify the NTP's message authentication code appended to each NTP packet header. 
                id: NTP symmetric authentication key identifier or index number (ID). This ID is included in the NTP cryptographic hash encoded header. 
                value: A hexadecimal digit string that represents the cryptographic key that is shared with the remote NTP server. The current expected length is 40 characters. </br> Use the cryptographic key and key ID to create a unique hash value used to authenticate the rest of the NTP data. 
            """

            kwargs = {}
            if digest_type is not None:
                kwargs["digest_type"] = digest_type
            if id is not None:
                kwargs["id"] = id
            if value is not None:
                kwargs["value"] = value

            if hasattr(NtpKey, "find"):
                resource = NtpKey.find(
                    **kwargs
                )
            else:
                resource = NtpKey()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete NtpKey: %s" % err)


