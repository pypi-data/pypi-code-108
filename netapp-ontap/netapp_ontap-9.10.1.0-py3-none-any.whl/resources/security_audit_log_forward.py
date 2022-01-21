r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
This API controls the forwarding of audit log information to remote syslog/splunk servers. Multiple destinations can be configured and all audit records are forwarded to all destinations.</br>
A GET operation retrieves information about remote syslog/splunk server destinations.
A POST operation creates a remote syslog/splunk server destination.
A GET operation on /security/audit/destinations/{address}/{port} retrieves information about the syslog/splunk server destination given its address and port number.
A PATCH operation on /security/audit/destinations/{address}/{port} updates information about the syslog/splunk server destination given its address and port number.
A DELETE operation on /security/audit/destinations/{address}/{port} deletes a syslog/splunk server destination given its address and port number.
### Overview of fields used for creating a remote syslog/splunk destination
The fields used for creating a remote syslog/splunk destination fall into the following categories
#### Required properties
All of the following fields are required for creating a remote syslog/splunk destination

* `address`
#### Optional properties
All of the following fields are optional for creating a remote syslog/splunk destination

* `port`
* `protocol`
* `facility`
* `verify_server`
<br />
---
## Examples
### Retrieving remote syslog/splunk server destinations
The following example shows remote syslog/splunk server destinations
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityAuditLogForward

with HostConnection(
    "<cluster-ip>", username="admin", password="password", verify=False
):
    print(list(SecurityAuditLogForward.get_collection()))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[SecurityAuditLogForward({"port": 514, "address": "1.1.1.1"})]

```
</div>
</div>

---
### Creating remote syslog/splunk server destinations
The following example creates remote syslog/splunk server destinations.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityAuditLogForward

with HostConnection(
    "<cluster-ip>", username="admin", password="password", verify=False
):
    resource = SecurityAuditLogForward()
    resource.address = "1.1.1.1"
    resource.port = 514
    resource.protocol = "udp_unencrypted"
    resource.facility = "kern"
    resource.post(hydrate=True, force=True)
    print(resource)

```

---
### Retrieving a remote syslog/splunk server destination given its destination address and port number
The following example retrieves a remote syslog/splunk server destination given its destination address and port number.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityAuditLogForward

with HostConnection(
    "<cluster-ip>", username="admin", password="password", verify=False
):
    resource = SecurityAuditLogForward(port=514, address="1.1.1.1")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
SecurityAuditLogForward(
    {
        "facility": "kern",
        "port": 514,
        "verify_server": False,
        "protocol": "udp_unencrypted",
        "address": "1.1.1.1",
    }
)

```
</div>
</div>

---
### Updating a remote syslog/splunk server destination given its destination address and port number
The following example updates a remote syslog/splunk server destination configuration given its destination address and port number.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityAuditLogForward

with HostConnection(
    "<cluster-ip>", username="admin", password="password", verify=False
):
    resource = SecurityAuditLogForward(port=514, address="1.1.1.1")
    resource.facility = "user"
    resource.patch()

```

---
### Deleting a remote syslog/splunk server destination given its destination address and port number
The following example deletes a remote syslog/splunk server destination configuration given its destination address and port number.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityAuditLogForward

with HostConnection(
    "<cluster-ip>", username="admin", password="password", verify=False
):
    resource = SecurityAuditLogForward(port=514, address="1.1.1.1")
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


__all__ = ["SecurityAuditLogForward", "SecurityAuditLogForwardSchema"]
__pdoc__ = {
    "SecurityAuditLogForwardSchema.resource": False,
    "SecurityAuditLogForward.security_audit_log_forward_show": False,
    "SecurityAuditLogForward.security_audit_log_forward_create": False,
    "SecurityAuditLogForward.security_audit_log_forward_modify": False,
    "SecurityAuditLogForward.security_audit_log_forward_delete": False,
}


class SecurityAuditLogForwardSchema(ResourceSchema):
    """The fields of the SecurityAuditLogForward object"""

    address = fields.Str(
        data_key="address",
    )
    r""" Destination syslog|splunk host to forward audit records to. This can be an IP address (IPv4|IPv6) or a hostname. """

    facility = fields.Str(
        data_key="facility",
        validate=enum_validation(['kern', 'user', 'local0', 'local1', 'local2', 'local3', 'local4', 'local5', 'local6', 'local7']),
    )
    r""" This is the standard Syslog Facility value that is used when sending audit records to a remote server.

Valid choices:

* kern
* user
* local0
* local1
* local2
* local3
* local4
* local5
* local6
* local7 """

    port = Size(
        data_key="port",
    )
    r""" Destination Port. The default port depends on the protocol chosen:
For un-encrypted destinations the default port is 514.
For encrypted destinations the default port is 6514. """

    protocol = fields.Str(
        data_key="protocol",
        validate=enum_validation(['udp_unencrypted', 'tcp_unencrypted', 'tcp_encrypted']),
    )
    r""" Log forwarding protocol

Valid choices:

* udp_unencrypted
* tcp_unencrypted
* tcp_encrypted """

    verify_server = fields.Boolean(
        data_key="verify_server",
    )
    r""" This is only applicable when the protocol is tcp_encrypted. This controls whether the remote server's certificate is validated. Setting "verify_server" to "true" will enforce validation of remote server's certificate. Setting "verify_server" to "false" will not enforce validation of remote server's certificate. """

    @property
    def resource(self):
        return SecurityAuditLogForward

    gettable_fields = [
        "address",
        "facility",
        "port",
        "protocol",
        "verify_server",
    ]
    """address,facility,port,protocol,verify_server,"""

    patchable_fields = [
        "facility",
        "verify_server",
    ]
    """facility,verify_server,"""

    postable_fields = [
        "address",
        "facility",
        "port",
        "protocol",
        "verify_server",
    ]
    """address,facility,port,protocol,verify_server,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SecurityAuditLogForward.get_collection(fields=field)]
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
            raise NetAppRestError("SecurityAuditLogForward modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SecurityAuditLogForward(Resource):
    """Allows interaction with SecurityAuditLogForward objects on the host"""

    _schema = SecurityAuditLogForwardSchema
    _path = "/api/security/audit/destinations"
    _keys = ["address", "port"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Defines a remote syslog/splunk server for sending audit information to.
### Learn more
* [`DOC /security/audit/destinations`](#docs-security-security_audit_destinations)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security audit log forward show")
        def security_audit_log_forward_show(
            fields: List[Choices.define(["address", "facility", "port", "protocol", "verify_server", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SecurityAuditLogForward resources

            Args:
                address: Destination syslog|splunk host to forward audit records to. This can be an IP address (IPv4|IPv6) or a hostname.
                facility: This is the standard Syslog Facility value that is used when sending audit records to a remote server.
                port: Destination Port. The default port depends on the protocol chosen: For un-encrypted destinations the default port is 514. For encrypted destinations the default port is 6514. 
                protocol: Log forwarding protocol
                verify_server: This is only applicable when the protocol is tcp_encrypted. This controls whether the remote server's certificate is validated. Setting \"verify_server\" to \"true\" will enforce validation of remote server's certificate. Setting \"verify_server\" to \"false\" will not enforce validation of remote server's certificate.
            """

            kwargs = {}
            if address is not None:
                kwargs["address"] = address
            if facility is not None:
                kwargs["facility"] = facility
            if port is not None:
                kwargs["port"] = port
            if protocol is not None:
                kwargs["protocol"] = protocol
            if verify_server is not None:
                kwargs["verify_server"] = verify_server
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SecurityAuditLogForward.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SecurityAuditLogForward resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["SecurityAuditLogForward"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates remote syslog/splunk server information.
### Learn more
* [`DOC /security/audit/destinations`](#docs-security-security_audit_destinations)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["SecurityAuditLogForward"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["SecurityAuditLogForward"], NetAppResponse]:
        r"""Configures remote syslog/splunk server information.
### Required properties
All of the following fields are required for creating a remote syslog/splunk destination
* `address`
### Optional properties
All of the following fields are optional for creating a remote syslog/splunk destination
* `port`
* `protocol`
* `facility`
* `verify_server` (Can only be "true" when protocol is "tcp_encrypted")

### Learn more
* [`DOC /security/audit/destinations`](#docs-security-security_audit_destinations)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["SecurityAuditLogForward"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes remote syslog/splunk server information.
### Learn more
* [`DOC /security/audit/destinations`](#docs-security-security_audit_destinations)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Defines a remote syslog/splunk server for sending audit information to.
### Learn more
* [`DOC /security/audit/destinations`](#docs-security-security_audit_destinations)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Defines a remote syslog/splunk server for sending audit information to.
### Learn more
* [`DOC /security/audit/destinations`](#docs-security-security_audit_destinations)"""
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
        r"""Configures remote syslog/splunk server information.
### Required properties
All of the following fields are required for creating a remote syslog/splunk destination
* `address`
### Optional properties
All of the following fields are optional for creating a remote syslog/splunk destination
* `port`
* `protocol`
* `facility`
* `verify_server` (Can only be "true" when protocol is "tcp_encrypted")

### Learn more
* [`DOC /security/audit/destinations`](#docs-security-security_audit_destinations)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security audit log forward create")
        async def security_audit_log_forward_create(
        ) -> ResourceTable:
            """Create an instance of a SecurityAuditLogForward resource

            Args:
                address: Destination syslog|splunk host to forward audit records to. This can be an IP address (IPv4|IPv6) or a hostname.
                facility: This is the standard Syslog Facility value that is used when sending audit records to a remote server.
                port: Destination Port. The default port depends on the protocol chosen: For un-encrypted destinations the default port is 514. For encrypted destinations the default port is 6514. 
                protocol: Log forwarding protocol
                verify_server: This is only applicable when the protocol is tcp_encrypted. This controls whether the remote server's certificate is validated. Setting \"verify_server\" to \"true\" will enforce validation of remote server's certificate. Setting \"verify_server\" to \"false\" will not enforce validation of remote server's certificate.
            """

            kwargs = {}
            if address is not None:
                kwargs["address"] = address
            if facility is not None:
                kwargs["facility"] = facility
            if port is not None:
                kwargs["port"] = port
            if protocol is not None:
                kwargs["protocol"] = protocol
            if verify_server is not None:
                kwargs["verify_server"] = verify_server

            resource = SecurityAuditLogForward(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SecurityAuditLogForward: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates remote syslog/splunk server information.
### Learn more
* [`DOC /security/audit/destinations`](#docs-security-security_audit_destinations)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security audit log forward modify")
        async def security_audit_log_forward_modify(
        ) -> ResourceTable:
            """Modify an instance of a SecurityAuditLogForward resource

            Args:
                address: Destination syslog|splunk host to forward audit records to. This can be an IP address (IPv4|IPv6) or a hostname.
                query_address: Destination syslog|splunk host to forward audit records to. This can be an IP address (IPv4|IPv6) or a hostname.
                facility: This is the standard Syslog Facility value that is used when sending audit records to a remote server.
                query_facility: This is the standard Syslog Facility value that is used when sending audit records to a remote server.
                port: Destination Port. The default port depends on the protocol chosen: For un-encrypted destinations the default port is 514. For encrypted destinations the default port is 6514. 
                query_port: Destination Port. The default port depends on the protocol chosen: For un-encrypted destinations the default port is 514. For encrypted destinations the default port is 6514. 
                protocol: Log forwarding protocol
                query_protocol: Log forwarding protocol
                verify_server: This is only applicable when the protocol is tcp_encrypted. This controls whether the remote server's certificate is validated. Setting \"verify_server\" to \"true\" will enforce validation of remote server's certificate. Setting \"verify_server\" to \"false\" will not enforce validation of remote server's certificate.
                query_verify_server: This is only applicable when the protocol is tcp_encrypted. This controls whether the remote server's certificate is validated. Setting \"verify_server\" to \"true\" will enforce validation of remote server's certificate. Setting \"verify_server\" to \"false\" will not enforce validation of remote server's certificate.
            """

            kwargs = {}
            changes = {}
            if query_address is not None:
                kwargs["address"] = query_address
            if query_facility is not None:
                kwargs["facility"] = query_facility
            if query_port is not None:
                kwargs["port"] = query_port
            if query_protocol is not None:
                kwargs["protocol"] = query_protocol
            if query_verify_server is not None:
                kwargs["verify_server"] = query_verify_server

            if address is not None:
                changes["address"] = address
            if facility is not None:
                changes["facility"] = facility
            if port is not None:
                changes["port"] = port
            if protocol is not None:
                changes["protocol"] = protocol
            if verify_server is not None:
                changes["verify_server"] = verify_server

            if hasattr(SecurityAuditLogForward, "find"):
                resource = SecurityAuditLogForward.find(
                    **kwargs
                )
            else:
                resource = SecurityAuditLogForward()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify SecurityAuditLogForward: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes remote syslog/splunk server information.
### Learn more
* [`DOC /security/audit/destinations`](#docs-security-security_audit_destinations)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security audit log forward delete")
        async def security_audit_log_forward_delete(
        ) -> None:
            """Delete an instance of a SecurityAuditLogForward resource

            Args:
                address: Destination syslog|splunk host to forward audit records to. This can be an IP address (IPv4|IPv6) or a hostname.
                facility: This is the standard Syslog Facility value that is used when sending audit records to a remote server.
                port: Destination Port. The default port depends on the protocol chosen: For un-encrypted destinations the default port is 514. For encrypted destinations the default port is 6514. 
                protocol: Log forwarding protocol
                verify_server: This is only applicable when the protocol is tcp_encrypted. This controls whether the remote server's certificate is validated. Setting \"verify_server\" to \"true\" will enforce validation of remote server's certificate. Setting \"verify_server\" to \"false\" will not enforce validation of remote server's certificate.
            """

            kwargs = {}
            if address is not None:
                kwargs["address"] = address
            if facility is not None:
                kwargs["facility"] = facility
            if port is not None:
                kwargs["port"] = port
            if protocol is not None:
                kwargs["protocol"] = protocol
            if verify_server is not None:
                kwargs["verify_server"] = verify_server

            if hasattr(SecurityAuditLogForward, "find"):
                resource = SecurityAuditLogForward.find(
                    **kwargs
                )
            else:
                resource = SecurityAuditLogForward()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete SecurityAuditLogForward: %s" % err)


