r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Defines, retrieves or deletes an individual SNMP traphost.
## Examples
### Retrieves an individual traphost in the cluster
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SnmpTraphost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SnmpTraphost(host="10.235.36.62")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
SnmpTraphost(
    {
        "host": "scspr0651011001.gdl.englab.netapp.com",
        "ip_address": "10.235.36.62",
        "user": {
            "name": "public",
            "_links": {
                "self": {
                    "href": "/api/support/snmp/users/800003150558b57e8dbd9ce9119d82005056a7b4e5/public"
                }
            },
        },
        "_links": {"self": {"href": "/api/support/snmp/traphosts/10.235.36.62"}},
    }
)

```
</div>
</div>

<br/>
### Deletes an individual traphost in the cluster
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SnmpTraphost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SnmpTraphost(host="3ffe:ffff:100:f102::1")
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


__all__ = ["SnmpTraphost", "SnmpTraphostSchema"]
__pdoc__ = {
    "SnmpTraphostSchema.resource": False,
    "SnmpTraphost.snmp_traphost_show": False,
    "SnmpTraphost.snmp_traphost_create": False,
    "SnmpTraphost.snmp_traphost_modify": False,
    "SnmpTraphost.snmp_traphost_delete": False,
}


class SnmpTraphostSchema(ResourceSchema):
    """The fields of the SnmpTraphost object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the snmp_traphost. """

    host = fields.Str(
        data_key="host",
    )
    r""" Fully qualified domain name (FQDN), IPv4 address or IPv6 address of SNMP traphost.

Example: traphost.example.com """

    ip_address = fields.Str(
        data_key="ip_address",
    )
    r""" The ip_address field of the snmp_traphost. """

    user = fields.Nested("netapp_ontap.resources.snmp_user.SnmpUserSchema", data_key="user", unknown=EXCLUDE)
    r""" The user field of the snmp_traphost. """

    @property
    def resource(self):
        return SnmpTraphost

    gettable_fields = [
        "links",
        "host",
        "ip_address",
        "user.links",
        "user.name",
    ]
    """links,host,ip_address,user.links,user.name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "host",
        "ip_address",
        "user.name",
    ]
    """host,ip_address,user.name,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SnmpTraphost.get_collection(fields=field)]
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
            raise NetAppRestError("SnmpTraphost modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SnmpTraphost(Resource):
    r""" SNMP manager or host machine that receives SNMP traps from ONTAP. """

    _schema = SnmpTraphostSchema
    _path = "/api/support/snmp/traphosts"
    _keys = ["host"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the list of SNMP traphosts along with the SNMP users configured for those traphosts.
### Related ONTAP commands
* `system snmp traphost show`
### Learn more
* [`DOC /support/snmp/traphosts`](#docs-support-support_snmp_traphosts)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snmp traphost show")
        def snmp_traphost_show(
            fields: List[Choices.define(["host", "ip_address", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SnmpTraphost resources

            Args:
                host: Fully qualified domain name (FQDN), IPv4 address or IPv6 address of SNMP traphost.
                ip_address: 
            """

            kwargs = {}
            if host is not None:
                kwargs["host"] = host
            if ip_address is not None:
                kwargs["ip_address"] = ip_address
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SnmpTraphost.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SnmpTraphost resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["SnmpTraphost"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["SnmpTraphost"], NetAppResponse]:
        r"""Creates SNMP traphosts. While adding an SNMPv3 traphost, an SNMPv3 user configured in ONTAP must be specified. ONTAP uses this user's credentials to authenticate and/or encrypt traps sent to this SNMPv3 traphost. While adding an SNMPv1/SNMPv2c traphost, SNMPv1/SNMPv2c user or community need not be specified.
### Required properties
* `host` - Fully Qualified Domain Name (FQDN), IPv4 address or IPv6 address of SNMP traphost.
### Recommended optional properties
* If `host` refers to an SNMPv3 traphost, the following field is required:
  * `user` - SNMPv3 or User-based Security Model (USM) user.
* For an SNMPv1/SNMPv2c traphost, ONTAP automatically uses 'public' if 'public' is configured or no community is configured. Otherwise, ONTAP uses the first configured community.
### Related ONTAP commands
* `system snmp traphost add`
### Learn more
* [`DOC /support/snmp/traphosts`](#docs-support-support_snmp_traphosts)
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
        records: Iterable["SnmpTraphost"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an SNMP traphost.
### Learn more
* [`DOC /support/snmp/traphosts/{host}`](#docs-support-support_snmp_traphosts_{host})
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the list of SNMP traphosts along with the SNMP users configured for those traphosts.
### Related ONTAP commands
* `system snmp traphost show`
### Learn more
* [`DOC /support/snmp/traphosts`](#docs-support-support_snmp_traphosts)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the details of an SNMP traphost along with the SNMP user configured for that traphost.
### Learn more
* [`DOC /support/snmp/traphosts/{host}`](#docs-support-support_snmp_traphosts_{host})
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
        r"""Creates SNMP traphosts. While adding an SNMPv3 traphost, an SNMPv3 user configured in ONTAP must be specified. ONTAP uses this user's credentials to authenticate and/or encrypt traps sent to this SNMPv3 traphost. While adding an SNMPv1/SNMPv2c traphost, SNMPv1/SNMPv2c user or community need not be specified.
### Required properties
* `host` - Fully Qualified Domain Name (FQDN), IPv4 address or IPv6 address of SNMP traphost.
### Recommended optional properties
* If `host` refers to an SNMPv3 traphost, the following field is required:
  * `user` - SNMPv3 or User-based Security Model (USM) user.
* For an SNMPv1/SNMPv2c traphost, ONTAP automatically uses 'public' if 'public' is configured or no community is configured. Otherwise, ONTAP uses the first configured community.
### Related ONTAP commands
* `system snmp traphost add`
### Learn more
* [`DOC /support/snmp/traphosts`](#docs-support-support_snmp_traphosts)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snmp traphost create")
        async def snmp_traphost_create(
        ) -> ResourceTable:
            """Create an instance of a SnmpTraphost resource

            Args:
                links: 
                host: Fully qualified domain name (FQDN), IPv4 address or IPv6 address of SNMP traphost.
                ip_address: 
                user: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if host is not None:
                kwargs["host"] = host
            if ip_address is not None:
                kwargs["ip_address"] = ip_address
            if user is not None:
                kwargs["user"] = user

            resource = SnmpTraphost(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SnmpTraphost: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an SNMP traphost.
### Learn more
* [`DOC /support/snmp/traphosts/{host}`](#docs-support-support_snmp_traphosts_{host})
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snmp traphost delete")
        async def snmp_traphost_delete(
        ) -> None:
            """Delete an instance of a SnmpTraphost resource

            Args:
                host: Fully qualified domain name (FQDN), IPv4 address or IPv6 address of SNMP traphost.
                ip_address: 
            """

            kwargs = {}
            if host is not None:
                kwargs["host"] = host
            if ip_address is not None:
                kwargs["ip_address"] = ip_address

            if hasattr(SnmpTraphost, "find"):
                resource = SnmpTraphost.find(
                    **kwargs
                )
            else:
                resource = SnmpTraphost()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete SnmpTraphost: %s" % err)


