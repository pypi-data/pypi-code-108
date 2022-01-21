r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
The Event Management System (EMS) collects and processes events, and sends notification of the events through various reporting mechanisms. The following endpoints defined under '/support/ems', allow you to query a list of observed events, and configure which events you handle and how you are notified:
- /support/ems
- /support/ems/events
- /support/ems/messages
- /support/ems/filters
- /support/ems/filters/{name}/rules
- /support/ems/filters/{name}/rules/{index}
- /support/ems/destinations
- /support/ems/destinations/{name}
## Examples
### Configuring an email destination
The following example configures EMS to send a support email when a WAFL event is observed with an error severity.
#### Configure the system-wide email parameters
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import EmsConfig

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = EmsConfig()
    resource.mail_from = "administrator@mycompany.com"
    resource.mail_server = "smtp@mycompany.com"
    resource.patch()

```

### Configuring a filter with an enclosed rule
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import EmsFilter

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = EmsFilter()
    resource.name = "critical-wafl"
    resource.rules = [
        {
            "index": 1,
            "type": "include",
            "message_criteria": {
                "name_pattern": "wafl.*",
                "severities": "emergency,error,alert",
            },
        }
    ]
    resource.post(hydrate=True)
    print(resource)

```

### Setting up an email destination
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import EmsDestination

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = EmsDestination()
    resource.name = "Technician_Email"
    resource.type = "email"
    resource.destination = "technician@mycompany.com"
    resource.filters = [{"name": "critical-wafl"}]
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


__all__ = ["EmsConfig", "EmsConfigSchema"]
__pdoc__ = {
    "EmsConfigSchema.resource": False,
    "EmsConfig.ems_config_show": False,
    "EmsConfig.ems_config_create": False,
    "EmsConfig.ems_config_modify": False,
    "EmsConfig.ems_config_delete": False,
}


class EmsConfigSchema(ResourceSchema):
    """The fields of the EmsConfig object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the ems_config. """

    mail_from = fields.Str(
        data_key="mail_from",
    )
    r""" Mail from

Example: administrator@mycompany.com """

    mail_server = fields.Str(
        data_key="mail_server",
    )
    r""" Mail server (SMTP)

Example: mail@mycompany.com """

    proxy_password = fields.Str(
        data_key="proxy_password",
    )
    r""" Password for HTTP/HTTPS proxy

Example: password """

    proxy_url = fields.Str(
        data_key="proxy_url",
    )
    r""" HTTP/HTTPS proxy URL

Example: https://proxyserver.mycompany.com """

    proxy_user = fields.Str(
        data_key="proxy_user",
    )
    r""" User name for HTTP/HTTPS proxy

Example: proxy_user """

    pubsub_enabled = fields.Boolean(
        data_key="pubsub_enabled",
    )
    r""" Is Publish/Subscribe Messaging Enabled?

Example: true """

    @property
    def resource(self):
        return EmsConfig

    gettable_fields = [
        "links",
        "mail_from",
        "mail_server",
        "proxy_url",
        "proxy_user",
        "pubsub_enabled",
    ]
    """links,mail_from,mail_server,proxy_url,proxy_user,pubsub_enabled,"""

    patchable_fields = [
        "mail_from",
        "mail_server",
        "proxy_password",
        "proxy_url",
        "proxy_user",
        "pubsub_enabled",
    ]
    """mail_from,mail_server,proxy_password,proxy_url,proxy_user,pubsub_enabled,"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in EmsConfig.get_collection(fields=field)]
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
            raise NetAppRestError("EmsConfig modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class EmsConfig(Resource):
    """Allows interaction with EmsConfig objects on the host"""

    _schema = EmsConfigSchema
    _path = "/api/support/ems"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the EMS configuration.
### Related ONTAP commands
* `event config show`

### Learn more
* [`DOC /support/ems`](#docs-support-support_ems)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems config show")
        def ems_config_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single EmsConfig resource

            Args:
                mail_from: Mail from
                mail_server: Mail server (SMTP)
                proxy_password: Password for HTTP/HTTPS proxy
                proxy_url: HTTP/HTTPS proxy URL
                proxy_user: User name for HTTP/HTTPS proxy
                pubsub_enabled: Is Publish/Subscribe Messaging Enabled?
            """

            kwargs = {}
            if mail_from is not None:
                kwargs["mail_from"] = mail_from
            if mail_server is not None:
                kwargs["mail_server"] = mail_server
            if proxy_password is not None:
                kwargs["proxy_password"] = proxy_password
            if proxy_url is not None:
                kwargs["proxy_url"] = proxy_url
            if proxy_user is not None:
                kwargs["proxy_user"] = proxy_user
            if pubsub_enabled is not None:
                kwargs["pubsub_enabled"] = pubsub_enabled
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = EmsConfig(
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
        r"""Updates the EMS configuration.
### Related ONTAP commands
* `event config modify`

### Learn more
* [`DOC /support/ems`](#docs-support-support_ems)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems config modify")
        async def ems_config_modify(
        ) -> ResourceTable:
            """Modify an instance of a EmsConfig resource

            Args:
                mail_from: Mail from
                query_mail_from: Mail from
                mail_server: Mail server (SMTP)
                query_mail_server: Mail server (SMTP)
                proxy_password: Password for HTTP/HTTPS proxy
                query_proxy_password: Password for HTTP/HTTPS proxy
                proxy_url: HTTP/HTTPS proxy URL
                query_proxy_url: HTTP/HTTPS proxy URL
                proxy_user: User name for HTTP/HTTPS proxy
                query_proxy_user: User name for HTTP/HTTPS proxy
                pubsub_enabled: Is Publish/Subscribe Messaging Enabled?
                query_pubsub_enabled: Is Publish/Subscribe Messaging Enabled?
            """

            kwargs = {}
            changes = {}
            if query_mail_from is not None:
                kwargs["mail_from"] = query_mail_from
            if query_mail_server is not None:
                kwargs["mail_server"] = query_mail_server
            if query_proxy_password is not None:
                kwargs["proxy_password"] = query_proxy_password
            if query_proxy_url is not None:
                kwargs["proxy_url"] = query_proxy_url
            if query_proxy_user is not None:
                kwargs["proxy_user"] = query_proxy_user
            if query_pubsub_enabled is not None:
                kwargs["pubsub_enabled"] = query_pubsub_enabled

            if mail_from is not None:
                changes["mail_from"] = mail_from
            if mail_server is not None:
                changes["mail_server"] = mail_server
            if proxy_password is not None:
                changes["proxy_password"] = proxy_password
            if proxy_url is not None:
                changes["proxy_url"] = proxy_url
            if proxy_user is not None:
                changes["proxy_user"] = proxy_user
            if pubsub_enabled is not None:
                changes["pubsub_enabled"] = pubsub_enabled

            if hasattr(EmsConfig, "find"):
                resource = EmsConfig.find(
                    **kwargs
                )
            else:
                resource = EmsConfig()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify EmsConfig: %s" % err)



