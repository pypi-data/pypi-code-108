r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
AutoSupport is the NetApp *call home* mechanism. AutoSupport sends configuration details, status details, and error reporting details to NetApp.<p/>
This endpoint supports both GET and PATCH calls. GET is used to retrieve AutoSupport configuration details for the cluster and PATCH is used to modify the AutoSupport configuration of the cluster. You can also use GET calls to check AutoSupport connectivity.
---
## Examples
### Configuring 'to' addresses
The following example configures AutoSupport to send emails to 'to' addresses.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Autosupport

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Autosupport()
    resource.to = ["abc@netapp.com", "xyz@netapp.com"]
    resource.patch()

```

---
### Configuring 'SMTP' transport
The following example configures AutoSupport to use 'SMTP' transport. The default transport is 'HTTPS'.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Autosupport

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Autosupport()
    resource.transport = "smtp"
    resource.patch()

```

---
### Retrieving the AutoSupport configuration
The following example retrieves AutoSupport configuration for the cluster.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Autosupport

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Autosupport()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
Autosupport(
    {
        "contact_support": True,
        "enabled": True,
        "mail_hosts": ["mailhost"],
        "is_minimal": False,
        "to": ["abc@netapp.com", "xyz@netapp.com"],
        "from": "Postmaster",
        "proxy_url": "",
        "transport": "smtp",
    }
)

```
</div>
</div>

---
### Retrieving AutoSupport connectivity issues
The following example retrieves AutoSupport connectivity issues for the cluster. The `fields=issues` parameter must be specified, for the response to return connectivity issues. The `corrective_action` section might contain commands which needs to be executed on the ONTAP CLI.<p/>
Note that the connectivity check can take up to 10 seconds to complete.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Autosupport

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Autosupport()
    resource.get(fields="issues")
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
Autosupport(
    {
        "issues": [
            {
                "corrective_action": {
                    "code": "53149746",
                    "message": "Check the hostname of the SMTP server",
                },
                "node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/0ecfd0a6-f1b3-11e8-9d9f-005056bbaadc"
                        }
                    },
                    "uuid": "0ecfd0a6-f1b3-11e8-9d9f-005056bbaadc",
                    "name": "node3",
                },
                "issue": {
                    "code": "53149746",
                    "message": "SMTP connectivity check failed for destination: mailhost. Error: Could not resolve host - 'mailhost'",
                },
            },
            {
                "corrective_action": {
                    "code": "53149740",
                    "message": 'Run "system node autosupport modify -transport https -node <node name>" to set "-transport" to "https".',
                },
                "node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/0ecfd0a6-f1b3-11e8-9d9f-005056bbaadc"
                        }
                    },
                    "uuid": "0ecfd0a6-f1b3-11e8-9d9f-005056bbaadc",
                    "name": "node3",
                },
                "issue": {
                    "code": "53149740",
                    "message": 'AutoSupport OnDemand is disabled when "-transport" is not set to "https".',
                },
            },
        ]
    }
)

```
</div>
</div>

---
### Retrieving AutoSupport configuration and connectivity issues
The following example retrieves AutoSupport configuration and connectivity issues on the cluster. Use `fields=*,issues` parameter to return both configuration and connectivity issues.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Autosupport

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Autosupport()
    resource.get(fields="*,issues")
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
Autosupport(
    {
        "contact_support": True,
        "enabled": True,
        "issues": [
            {
                "corrective_action": {
                    "code": "53149746",
                    "message": "Check the hostname of the SMTP server",
                },
                "node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/0ecfd0a6-f1b3-11e8-9d9f-005056bbaadc"
                        }
                    },
                    "uuid": "0ecfd0a6-f1b3-11e8-9d9f-005056bbaadc",
                    "name": "node3",
                },
                "issue": {
                    "code": "53149746",
                    "message": "SMTP connectivity check failed for destination: mailhost. Error: Could not resolve host - 'mailhost'",
                },
            },
            {
                "corrective_action": {
                    "code": "53149740",
                    "message": 'Run "system node autosupport modify -transport https -node <node name>" to set "-transport" to "https".',
                },
                "node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/0ecfd0a6-f1b3-11e8-9d9f-005056bbaadc"
                        }
                    },
                    "uuid": "0ecfd0a6-f1b3-11e8-9d9f-005056bbaadc",
                    "name": "node3",
                },
                "issue": {
                    "code": "53149740",
                    "message": 'AutoSupport OnDemand is disabled when "-transport" is not set to "https".',
                },
            },
        ],
        "mail_hosts": ["mailhost"],
        "is_minimal": False,
        "to": ["abc@netapp.com", "xyz@netapp.com"],
        "from": "Postmaster",
        "proxy_url": "",
        "transport": "smtp",
    }
)

```
</div>
</div>

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


__all__ = ["Autosupport", "AutosupportSchema"]
__pdoc__ = {
    "AutosupportSchema.resource": False,
    "Autosupport.autosupport_show": False,
    "Autosupport.autosupport_create": False,
    "Autosupport.autosupport_modify": False,
    "Autosupport.autosupport_delete": False,
}


class AutosupportSchema(ResourceSchema):
    """The fields of the Autosupport object"""

    contact_support = fields.Boolean(
        data_key="contact_support",
    )
    r""" Specifies whether to send the AutoSupport messages to vendor support.

Example: true """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Specifies whether the AutoSupport daemon is enabled.  When this setting is disabled, delivery of all AutoSupport messages is turned off.

Example: true """

    from_ = fields.Str(
        data_key="from",
    )
    r""" The e-mail address from which the AutoSupport messages are sent. To generate node-specific 'from' addresses, enable '-node-specific-from' parameter via ONTAP CLI.

Example: postmaster@example.com """

    is_minimal = fields.Boolean(
        data_key="is_minimal",
    )
    r""" Specifies whether the system information is collected in compliant form, to remove private data or in complete form, to enhance diagnostics.

Example: true """

    issues = fields.List(fields.Nested("netapp_ontap.models.autosupport_issues.AutosupportIssuesSchema", unknown=EXCLUDE), data_key="issues")
    r""" A list of nodes in the cluster with connectivity issues to HTTP/SMTP/AOD AutoSupport destinations along with the corresponding error descriptions and corrective actions. """

    mail_hosts = fields.List(fields.Str, data_key="mail_hosts")
    r""" The names of the mail servers used to deliver AutoSupport messages via SMTP.

Example: ["mailhost1.example.com","mailhost2.example.com"] """

    partner_addresses = fields.List(fields.Str, data_key="partner_addresses")
    r""" The list of partner addresses.

Example: ["user1@partner.com","user2@partner.com"] """

    proxy_url = fields.Str(
        data_key="proxy_url",
    )
    r""" Proxy server for AutoSupport message delivery via HTTP/S. Optionally specify a username/password for authentication with the proxy server.

Example: https://proxy.company.com """

    to = fields.List(fields.Str, data_key="to")
    r""" The e-mail addresses to which the AutoSupport messages are sent.

Example: ["user1@example.com","user2@example.com"] """

    transport = fields.Str(
        data_key="transport",
        validate=enum_validation(['smtp', 'http', 'https']),
    )
    r""" The name of the transport protocol used to deliver AutoSupport messages.

Valid choices:

* smtp
* http
* https """

    @property
    def resource(self):
        return Autosupport

    gettable_fields = [
        "contact_support",
        "enabled",
        "from_",
        "is_minimal",
        "issues",
        "mail_hosts",
        "partner_addresses",
        "proxy_url",
        "to",
        "transport",
    ]
    """contact_support,enabled,from_,is_minimal,issues,mail_hosts,partner_addresses,proxy_url,to,transport,"""

    patchable_fields = [
        "contact_support",
        "enabled",
        "from_",
        "is_minimal",
        "mail_hosts",
        "partner_addresses",
        "proxy_url",
        "to",
        "transport",
    ]
    """contact_support,enabled,from_,is_minimal,mail_hosts,partner_addresses,proxy_url,to,transport,"""

    postable_fields = [
        "contact_support",
        "enabled",
        "from_",
        "is_minimal",
        "mail_hosts",
        "partner_addresses",
        "proxy_url",
        "to",
        "transport",
    ]
    """contact_support,enabled,from_,is_minimal,mail_hosts,partner_addresses,proxy_url,to,transport,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Autosupport.get_collection(fields=field)]
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
            raise NetAppRestError("Autosupport modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Autosupport(Resource):
    """Allows interaction with Autosupport objects on the host"""

    _schema = AutosupportSchema
    _path = "/api/support/autosupport"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the AutoSupport configuration of the cluster and if requested, returns connectivity issues with the AutoSupport configuration.<p/>
</br>Important note:
* The **issues** field consists of a list of objects containing details of the node that has a connectivity issue, the issue description, and corrective action you can take to address the issue. When not empty, this indicates a connection issue to the **HTTP/S**, **SMTP**, or **AutoSupport On Demand** server.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `issues`
### Related ONTAP commands
* `system node autosupport show -instance`
* `system node autosupport check show-details`
### Learn more
* [`DOC /support/autosupport`](#docs-support-support_autosupport)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="autosupport show")
        def autosupport_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single Autosupport resource

            Args:
                contact_support: Specifies whether to send the AutoSupport messages to vendor support.
                enabled: Specifies whether the AutoSupport daemon is enabled.  When this setting is disabled, delivery of all AutoSupport messages is turned off.
                from_: The e-mail address from which the AutoSupport messages are sent. To generate node-specific 'from' addresses, enable '-node-specific-from' parameter via ONTAP CLI.
                is_minimal: Specifies whether the system information is collected in compliant form, to remove private data or in complete form, to enhance diagnostics.
                mail_hosts: The names of the mail servers used to deliver AutoSupport messages via SMTP.
                partner_addresses: The list of partner addresses.
                proxy_url: Proxy server for AutoSupport message delivery via HTTP/S. Optionally specify a username/password for authentication with the proxy server.
                to: The e-mail addresses to which the AutoSupport messages are sent.
                transport: The name of the transport protocol used to deliver AutoSupport messages.
            """

            kwargs = {}
            if contact_support is not None:
                kwargs["contact_support"] = contact_support
            if enabled is not None:
                kwargs["enabled"] = enabled
            if from_ is not None:
                kwargs["from_"] = from_
            if is_minimal is not None:
                kwargs["is_minimal"] = is_minimal
            if mail_hosts is not None:
                kwargs["mail_hosts"] = mail_hosts
            if partner_addresses is not None:
                kwargs["partner_addresses"] = partner_addresses
            if proxy_url is not None:
                kwargs["proxy_url"] = proxy_url
            if to is not None:
                kwargs["to"] = to
            if transport is not None:
                kwargs["transport"] = transport
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = Autosupport(
                **kwargs
            )
            resource.get()
            return [resource]


    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the AutoSupport configuration for the entire cluster.
### Related ONTAP commands
* `system node autosupport modify`
### Learn more
* [`DOC /support/autosupport`](#docs-support-support_autosupport)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="autosupport modify")
        async def autosupport_modify(
        ) -> ResourceTable:
            """Modify an instance of a Autosupport resource

            Args:
                contact_support: Specifies whether to send the AutoSupport messages to vendor support.
                query_contact_support: Specifies whether to send the AutoSupport messages to vendor support.
                enabled: Specifies whether the AutoSupport daemon is enabled.  When this setting is disabled, delivery of all AutoSupport messages is turned off.
                query_enabled: Specifies whether the AutoSupport daemon is enabled.  When this setting is disabled, delivery of all AutoSupport messages is turned off.
                from_: The e-mail address from which the AutoSupport messages are sent. To generate node-specific 'from' addresses, enable '-node-specific-from' parameter via ONTAP CLI.
                query_from_: The e-mail address from which the AutoSupport messages are sent. To generate node-specific 'from' addresses, enable '-node-specific-from' parameter via ONTAP CLI.
                is_minimal: Specifies whether the system information is collected in compliant form, to remove private data or in complete form, to enhance diagnostics.
                query_is_minimal: Specifies whether the system information is collected in compliant form, to remove private data or in complete form, to enhance diagnostics.
                mail_hosts: The names of the mail servers used to deliver AutoSupport messages via SMTP.
                query_mail_hosts: The names of the mail servers used to deliver AutoSupport messages via SMTP.
                partner_addresses: The list of partner addresses.
                query_partner_addresses: The list of partner addresses.
                proxy_url: Proxy server for AutoSupport message delivery via HTTP/S. Optionally specify a username/password for authentication with the proxy server.
                query_proxy_url: Proxy server for AutoSupport message delivery via HTTP/S. Optionally specify a username/password for authentication with the proxy server.
                to: The e-mail addresses to which the AutoSupport messages are sent.
                query_to: The e-mail addresses to which the AutoSupport messages are sent.
                transport: The name of the transport protocol used to deliver AutoSupport messages.
                query_transport: The name of the transport protocol used to deliver AutoSupport messages.
            """

            kwargs = {}
            changes = {}
            if query_contact_support is not None:
                kwargs["contact_support"] = query_contact_support
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_from_ is not None:
                kwargs["from_"] = query_from_
            if query_is_minimal is not None:
                kwargs["is_minimal"] = query_is_minimal
            if query_mail_hosts is not None:
                kwargs["mail_hosts"] = query_mail_hosts
            if query_partner_addresses is not None:
                kwargs["partner_addresses"] = query_partner_addresses
            if query_proxy_url is not None:
                kwargs["proxy_url"] = query_proxy_url
            if query_to is not None:
                kwargs["to"] = query_to
            if query_transport is not None:
                kwargs["transport"] = query_transport

            if contact_support is not None:
                changes["contact_support"] = contact_support
            if enabled is not None:
                changes["enabled"] = enabled
            if from_ is not None:
                changes["from_"] = from_
            if is_minimal is not None:
                changes["is_minimal"] = is_minimal
            if mail_hosts is not None:
                changes["mail_hosts"] = mail_hosts
            if partner_addresses is not None:
                changes["partner_addresses"] = partner_addresses
            if proxy_url is not None:
                changes["proxy_url"] = proxy_url
            if to is not None:
                changes["to"] = to
            if transport is not None:
                changes["transport"] = transport

            if hasattr(Autosupport, "find"):
                resource = Autosupport.find(
                    **kwargs
                )
            else:
                resource = Autosupport()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify Autosupport: %s" % err)



