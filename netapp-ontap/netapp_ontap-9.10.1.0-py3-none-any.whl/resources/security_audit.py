r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
This API controls what is logged to the audit log files. All operations that make changes are always logged and cannot be disabled. The PATCH request updates administrative audit settings for GET requests. All fields are optional for a PATCH request. A GET request retrieves administrative audit settings for GET requests.
<br />
---
## Examples
### Retrieving administrative audit settings for GET requests
The following example shows the administrative audit settings for GET requests.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityAudit

with HostConnection(
    "<cluster-ip>", username="admin", password="password", verify=False
):
    resource = SecurityAudit()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
SecurityAudit({"cli": False, "http": False, "ontapi": False})

```
</div>
</div>

---
### Updating administrative audit settings for GET requests
The following example updates the administrative audit settings for GET requests
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityAudit

with HostConnection(
    "<cluster-ip>", username="admin", password="password", verify=False
):
    resource = SecurityAudit()
    resource.cli = False
    resource.http = True
    resource.ontapi = True
    resource.patch()

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


__all__ = ["SecurityAudit", "SecurityAuditSchema"]
__pdoc__ = {
    "SecurityAuditSchema.resource": False,
    "SecurityAudit.security_audit_show": False,
    "SecurityAudit.security_audit_create": False,
    "SecurityAudit.security_audit_modify": False,
    "SecurityAudit.security_audit_delete": False,
}


class SecurityAuditSchema(ResourceSchema):
    """The fields of the SecurityAudit object"""

    cli = fields.Boolean(
        data_key="cli",
    )
    r""" Enable auditing of CLI GET Operations. Valid in PATCH """

    http = fields.Boolean(
        data_key="http",
    )
    r""" Enable auditing of HTTP GET Operations. Valid in PATCH """

    ontapi = fields.Boolean(
        data_key="ontapi",
    )
    r""" Enable auditing of ONTAP API GET operations. Valid in PATCH """

    @property
    def resource(self):
        return SecurityAudit

    gettable_fields = [
        "cli",
        "http",
        "ontapi",
    ]
    """cli,http,ontapi,"""

    patchable_fields = [
        "cli",
        "http",
        "ontapi",
    ]
    """cli,http,ontapi,"""

    postable_fields = [
        "cli",
        "http",
        "ontapi",
    ]
    """cli,http,ontapi,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SecurityAudit.get_collection(fields=field)]
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
            raise NetAppRestError("SecurityAudit modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SecurityAudit(Resource):
    """Allows interaction with SecurityAudit objects on the host"""

    _schema = SecurityAuditSchema
    _path = "/api/security/audit"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves administrative audit settings for GET requests.
### Learn more
* [`DOC /security/audit`](#docs-security-security_audit)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security audit show")
        def security_audit_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single SecurityAudit resource

            Args:
                cli: Enable auditing of CLI GET Operations. Valid in PATCH
                http: Enable auditing of HTTP GET Operations. Valid in PATCH
                ontapi: Enable auditing of ONTAP API GET operations. Valid in PATCH
            """

            kwargs = {}
            if cli is not None:
                kwargs["cli"] = cli
            if http is not None:
                kwargs["http"] = http
            if ontapi is not None:
                kwargs["ontapi"] = ontapi
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = SecurityAudit(
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
        r"""Updates administrative audit settings for GET requests.
All of the fields are optional. An empty body will make no changes.

### Learn more
* [`DOC /security/audit`](#docs-security-security_audit)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security audit modify")
        async def security_audit_modify(
        ) -> ResourceTable:
            """Modify an instance of a SecurityAudit resource

            Args:
                cli: Enable auditing of CLI GET Operations. Valid in PATCH
                query_cli: Enable auditing of CLI GET Operations. Valid in PATCH
                http: Enable auditing of HTTP GET Operations. Valid in PATCH
                query_http: Enable auditing of HTTP GET Operations. Valid in PATCH
                ontapi: Enable auditing of ONTAP API GET operations. Valid in PATCH
                query_ontapi: Enable auditing of ONTAP API GET operations. Valid in PATCH
            """

            kwargs = {}
            changes = {}
            if query_cli is not None:
                kwargs["cli"] = query_cli
            if query_http is not None:
                kwargs["http"] = query_http
            if query_ontapi is not None:
                kwargs["ontapi"] = query_ontapi

            if cli is not None:
                changes["cli"] = cli
            if http is not None:
                changes["http"] = http
            if ontapi is not None:
                changes["ontapi"] = ontapi

            if hasattr(SecurityAudit, "find"):
                resource = SecurityAudit.find(
                    **kwargs
                )
            else:
                resource = SecurityAudit()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify SecurityAudit: %s" % err)



